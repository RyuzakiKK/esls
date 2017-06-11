package tests;

import static org.junit.Assert.*;

import org.junit.Test;

import main.MainService;

/**
 * JUnit tests for parseCommandLineParameters() method.
 * @author Eugenio
 * @version 1.0
 * @see MainService#parseCommandLineParameters(String[])
 */
public class TestParseCommandLineParameters {

	private static final int listenPortParamater = 9999;
	private static final String dbHostParameter = "10.0.0.1";
	private static final int dbPortParameter = 1234;
	private static final String dbNameParameter = "databaseName";
	private static final String certificatePathParameter = "DO_progetto_Smart_City_e_Isac.pfx";
	private static final String certificatePasswordParameter = "abcde";
	
	/**
	 * Tests the method overriding all parameters default values.
	 */
	@Test
	public void testFullOverride() {
		final String[] parameters = new String[] {"--listenport=" + listenPortParamater,
				"--dbhost=" + dbHostParameter,
				"--dbport=" + dbPortParameter,
				"--dbname=" + dbNameParameter,
				"--debug",
				"--certificatePath=" + certificatePathParameter,
				"--certificatePassword=" + certificatePasswordParameter};
		MainService.parseCommandLineParameters(parameters);
		assertEquals(MainService.getListenPort(), listenPortParamater);
		assertEquals(MainService.getDbHost(), dbHostParameter);
		assertEquals(MainService.getDbPort(), dbPortParameter);
		assertEquals(MainService.getDbName(), dbNameParameter);
		assertTrue(MainService.isDebug());
		assertEquals(MainService.getCertificatePath(), certificatePathParameter);
		assertEquals(MainService.getCertificatePassword(), certificatePasswordParameter);
	}
	
	/**
	 * Tests the method overriding only a few parameters, leaving the others at their default values.
	 */
	@Test
	public void testPartialOverride() {
		final String[] parameters = new String[] {"--listenport=" + listenPortParamater,
				"--certificatePath=" + certificatePathParameter,
				"--certificatePassword=" + certificatePasswordParameter};
		MainService.parseCommandLineParameters(parameters);
		assertEquals(MainService.getListenPort(), listenPortParamater);
		assertEquals(MainService.getDbHost(), "127.0.0.1");
		assertEquals(MainService.getDbPort(), 8086);
		assertEquals(MainService.getDbName(), "esls");
		assertFalse(MainService.isDebug());
		assertEquals(MainService.getCertificatePath(), certificatePathParameter);
		assertEquals(MainService.getCertificatePassword(), certificatePasswordParameter);
	}

}
