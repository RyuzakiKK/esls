package main;

/**
 * Enum containing the error types which can be used by the service.
 * @author Eugenio
 * @version 1.0
 */
public enum ErrorType {
	GENERIC;
	
	/**
	 * Converts an error code to the corresponding ErrorType value.
	 * @param errorCode The code which is parsed.
	 * @return The corresponding ErrorType value.
	 */
	public static ErrorType parseErrorType(int errorCode) {
		switch(errorCode) {
		case 1:
			return ErrorType.GENERIC;
		default:
			System.out.println("Illegal error code!");
			return null;
		}
	}
}
