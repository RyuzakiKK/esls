package tests;

import static org.junit.Assert.*;

import org.junit.Test;

import io.vertx.core.json.JsonObject;
import main.ActionType;

/**
 * JUnit tests to verify JSON messages parsing.
 * @author Eugenio
 * @version 1.0
 */
public class TestJsonParsing {
	
	private static final int action = ActionType.ON.ordinal();
	private static final String area = "test_area";
	private static final int intensity = 40;
	private static final int photoresistor = 60;
	private static final long timestamp = 1496673782;
	private static JsonObject jo;
		
	/**
	 * Tests JSON data parsing through JsonObject
	 */
	@Test
	public void test() {
		final String jsonData = "{\"action\":\"" + action + "\",\"area\":\"" + area + "\",\"intensity\":\"" + intensity + "\",\"photoresistor\":\"" + photoresistor + "\",\"timestamp\":\"" + timestamp + "\"}";
		jo = new JsonObject(jsonData);
		assertEquals(Integer.parseInt(jo.getString("action")), action);
		assertEquals(jo.getString("area"), area);
		assertEquals(Integer.parseInt(jo.getString("intensity")), intensity);
		assertEquals(Integer.parseInt(jo.getString("photoresistor")), photoresistor);
		assertEquals(Long.parseLong(jo.getString("timestamp")), timestamp);
	}

}
