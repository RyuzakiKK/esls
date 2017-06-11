/**
 * 
 */
package main;

/**
 * Interface for logging components.
 * @author Eugenio
 * @version 1.0
 */
public interface ILogger {
	
	/**
	 * Logs a message to the location specified in the implementation.
	 * @param message The message to log.
	 */
	void log(String message);
}
