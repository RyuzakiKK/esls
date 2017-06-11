package main;

/**
 * Enum containing the action types which can be used by the service.
 * @author Eugenio
 * @version 1.0
 */
public enum ActionType {
	ON, OFF, ENERGY, CAR;
	
	/**
	 * Converts an action code to the corresponding ActionType value.
	 * @param actionCode The code which is parsed.
	 * @return The corresponding ActionType value.
	 */
	public static ActionType parseActionType(int actionCode) {
		switch (actionCode) {
		case 1:
			return ActionType.ON;
		case 2:
			return ActionType.OFF;
		case 3:
			return ActionType.ENERGY;
		case 4:
			return ActionType.CAR;
		default:
			System.out.println("Illegal action code!");
			return null;
		}
	}
}