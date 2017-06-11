package main;

import java.io.File;

import io.vertx.core.Vertx;
import io.vertx.core.http.*;
import io.vertx.core.json.JsonObject;
import io.vertx.core.net.JksOptions;
import io.vertx.ext.web.Router;
import io.vertx.ext.web.handler.BodyHandler;

/**
 * Class containing the Vert.x main service.
 * @author Eugenio
 * @version 1.0
 */
public class MainService {

	private static final String MALFORMED_REQUEST_ERROR_MESSAGE = "Malformed request! It will be ignored. One or more parameters are invalid or missing.";
	private static final String API_LEVEL = "1.0";
	private static final long BODY_SIZE_LIMIT = 10240; // DDoS mitigation
	private static final ILogger logger = ConsoleLogger.getInstance(); // Logging component
	private static String dbHost = "127.0.0.1";
	private static int listenPort = 44343;
	private static int dbPort = 8086;
	private static String dbName = "esls";
	private static boolean debug = false;
	private static String certificatePath = "DO_progetto_Smart_City_e_Isac.pfx";
	private static String certificatePassword = "keystore5371";
	private static Vertx vertx = Vertx.vertx();
	
	// Getters and setters
	public static String getDbHost() {
		return dbHost;
	}

	public static void setDbHost(String dbHost) {
		MainService.dbHost = dbHost;
	}

	public static int getListenPort() {
		return listenPort;
	}

	public static void setListenPort(int listenPort) {
		MainService.listenPort = listenPort;
	}

	public static int getDbPort() {
		return dbPort;
	}

	public static void setDbPort(int dbPort) {
		MainService.dbPort = dbPort;
	}

	public static String getDbName() {
		return dbName;
	}

	public static void setDbName(String dbName) {
		MainService.dbName = dbName;
	}

	public static boolean isDebug() {
		return debug;
	}

	public static void setDebug(boolean debug) {
		MainService.debug = debug;
	}

	public static String getCertificatePath() {
		return certificatePath;
	}

	public static void setCertificatePath(String certificatePath) {
		MainService.certificatePath = certificatePath;
	}

	public static String getCertificatePassword() {
		return certificatePassword;
	}

	public static void setCertificatePassword(String certificatePassword) {
		MainService.certificatePassword = certificatePassword;
	}

	/**
	 * Start method for the service.
	 * @param args Command line parameters.
	 * @see MainService#parseCommandLineParameters(String[]) 
	 */
	public static void main(String[] args) {
		parseCommandLineParameters(args); // Reading command line parameters
		final Router router = Router.router(vertx);
		router.route().handler(BodyHandler.create().setBodyLimit(BODY_SIZE_LIMIT));
		
		// Default route
		router.route("/").handler(routingContext -> {
			HttpServerResponse response = routingContext.response();
			setResponseHeaders(response);
			response.end("<h1>404</h1>");
		});
				
		// Changed Light Intensity message
		router.route("/esls/api/" + API_LEVEL + "/changeLightIntensity*").handler(routingContext -> {
			HttpServerResponse response = routingContext.response();
			setResponseHeaders(response);
			response.end("<h1>200</h1>"); // TODO: restituire stato http?
			// Reading request parameters
			final JsonObject jo = new JsonObject(routingContext.getBodyAsString());
			if(debug) {
				logger.log("changeLightIntensity\n" + jo.encodePrettily());
			}
			ActionType actionEnum = null;
			String area = null;
			int intensity = 0, photoresistor = 0;
			long timestamp = 0;
			try {
				actionEnum = ActionType.parseActionType(Integer.parseInt(jo.getString("action")));
				area = jo.getString("area");
				intensity = Integer.parseInt(jo.getString("intensity"));
				photoresistor = Integer.parseInt(jo.getString("photoresistor"));
				timestamp = Long.parseLong(jo.getString("timestamp"));
				sendChangeLightIntensityToDatabase(routingContext.request().remoteAddress().host(), actionEnum, area, intensity, photoresistor, timestamp);
			} catch (NumberFormatException ex) {
				logger.log(MALFORMED_REQUEST_ERROR_MESSAGE);
			}
		});

		// Changed Policy message
		router.route("/esls/api/" + API_LEVEL + "/changePolicy*").handler(routingContext -> {
			HttpServerResponse response = routingContext.response();
			setResponseHeaders(response);
			response.end("<h1>200</h1>"); // TODO: restituire stato http?
			// Reading request parameters
			final JsonObject jo = new JsonObject(routingContext.getBodyAsString());
			if(debug) {
				logger.log("changePolicy\n" + jo.encodePrettily());
			}
			String area = null;
			long timestamp = 0;
			try {
				area = jo.getString("area");
				timestamp = Long.parseLong(jo.getString("timestamp"));
				// Possibily, save the log to a database instead of to console only.
			} catch (NumberFormatException ex) {
				logger.log(MALFORMED_REQUEST_ERROR_MESSAGE);
			}
		});
		
		// Error message
		router.route("/esls/api/" + API_LEVEL + "/notifyError*").handler(routingContext -> {
			HttpServerResponse response = routingContext.response();
			setResponseHeaders(response);
			response.end("<h1>200</h1>"); // TODO: restituire stato http?
			// Reading request parameters
			final JsonObject jo = new JsonObject(routingContext.getBodyAsString());
			if(debug) {
				logger.log("notifyError\n" + jo.encodePrettily());
			}
			ErrorType errorEnum = null;
			String area = null;
			long timestamp = 0;
			try {
				errorEnum = ErrorType.parseErrorType(Integer.parseInt(jo.getString("errorType")));
				area = jo.getString("area");
				timestamp = Long.parseLong(jo.getString("timestamp"));
				// Possibily, save the log to a database instead of to console only.
			} catch (NumberFormatException ex) {
				logger.log(MALFORMED_REQUEST_ERROR_MESSAGE);
			}	
		});

		vertx
		.createHttpServer(new HttpServerOptions()
				.setSsl(true)
				.setKeyStoreOptions(
						new JksOptions()
						.setPath(certificatePath)
						.setPassword(certificatePassword)
		))
		.requestHandler(router::accept)
		.listen(listenPort);
	}

	/**
	 * Reads the command line parameter and sets the corresponding variables.
	 * If incompatible values are given, the default values will be used.
	 * @param parameters The command line parameters to be read
	 */
	public static void parseCommandLineParameters(String[] parameters) {
		for(final String param : parameters) {
			if (param.startsWith("--listenport=")) {
				try {
					listenPort = Integer.parseInt(param.substring(13));
				} catch (NumberFormatException ex) {
					logger.log("Invalid listening port format!");
				}
			} else if (param.startsWith("--dbhost=")) {
				dbHost = param.substring(9);
			} else if (param.startsWith("--dbport=")) {
				try {
					dbPort = Integer.parseInt(param.substring(9));
				} catch (NumberFormatException ex) {
					logger.log("Invalid database port format!");
				}
			} else if (param.startsWith("--dbname=")) {
				dbName = param.substring(9);
			} else if (param.startsWith("--debug")) {
				debug = true;
			} else if (param.startsWith("--certificatePath=")) {
				final String certPath = param.substring(18);
				if(new File(certPath).exists()) {
					certificatePath = certPath;
				} else {
					logger.log("Invalid certificate file!");
				}
			} else if (param.startsWith("--certificatePassword=")) {
				certificatePassword = param.substring(22);
			} else {
				logger.log("Ignored invalid commmand line parameter: " + param);
			}
		}
	}
	
	/**
	 * Writes to InfluxDb a new "send change light intensity" record. 
	 * @param sourceHost The host which generated the message.
	 * @param action The action which generated the message.
	 * @param area The area where the host is.
	 * @param intensity The light intensity currently set.
	 * @param photoresistor The current measured light intensity.
	 * @param timestamp The unix timestamp (long, UTC) when the event happened. If it is set to "0", the server time will be used, instead.
	 */
	public static void sendChangeLightIntensityToDatabase(final String sourceHost, final ActionType action, final String area, final int intensity, final int photoresistor, final long timestamp) {
		final String optionalTimestamp = (timestamp == 0) ? "" : " " + timestamp; 
		final HttpClient client = vertx.createHttpClient();
		client.post(dbPort, dbHost, "/write?db=" + dbName, response -> {
			logger.log("Answer from database: " + response.statusCode());
		}).putHeader("content-type", "text/plain")
		.end("changeLightIntensity" + 
				",host=" + sourceHost +
				",area=" + area +
				" action=" + (action.ordinal()+1) +
				",intensity=" + intensity +
				",photoresistor=" + photoresistor +
				optionalTimestamp);
	}
	
	/**
	 * Sets HTTP headers to a HttpServerResponse.
	 * @param response The response to which the headers must be applied.
	 */
	private static void setResponseHeaders(final HttpServerResponse response) {
		response
		.putHeader("Cache-Control", "no-store, no-cache")
		.putHeader("X-Content-Type-Options", "nosniff")
		.putHeader("Strict-Transport-Security", "max-age=" + 15768000)
		.putHeader("X-Download-Options", "noopen")
		.putHeader("X-XSS-Protection", "1; mode=block")
		.putHeader("X-FRAME-OPTIONS", "DENY")
		.putHeader("content-type", "text/html");
	}
}
