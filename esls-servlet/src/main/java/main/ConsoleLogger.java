/**
 * 
 */
package main;

/**
 * Singleton class to log messages to the console.
 * @author Eugenio
 * @version 1.0
 */
public class ConsoleLogger implements ILogger {

	private static final ConsoleLogger SINGLETON = new ConsoleLogger();
	
	/**
	 * Private constructor (Singleton pattern).
	 */
	private ConsoleLogger() {
	}
	
	/**
	 * @return Current Singleton instance.
	 */
	public static ConsoleLogger getInstance() {
		return SINGLETON;
	}
	
	/**
	 * Logs a message to the console.
	 * @see ILogger#log(String)
	 */
	@Override
	public void log(String message) {
		System.out.println(message);
	}

}
