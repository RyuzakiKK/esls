/**
 * 
 */
package tests;

import static org.junit.Assert.*;

import org.junit.Test;

import main.ActionType;
import main.MainService;

/**
 * JUnit tests for sendChangeLightIntensityToDatabase() method.
 * @author Eugenio
 * @version 1.0
 * @see MainService#sendChangeLightIntensityToDatabase(String, main.ActionType, String, int, int, long)
 */
public class TestSendChangeLightIntensityToDatabase {

	private static final String sourceHost = "127.0.0.1";
	private static final ActionType action = ActionType.ON;
	private static final String area = "4";
	private static final int intensity = 40;
	private static final int photoresistor = 60;
	private static final long timestamp = 1496673782; 
	
	/**
	 * Tests for sendChangeLightIntensityToDatabase().
	 */
	@Test
	public void test() {
		MainService.sendChangeLightIntensityToDatabase(sourceHost, action, area, intensity, photoresistor, timestamp);
	}

}
