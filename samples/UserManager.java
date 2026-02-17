public class UserManager {
    public boolean validateUser(String username, String password) {
        if (username == null || username.isEmpty()) {
            return false;
        }
        if (password == null || password.length() < 8) {
            return false;
        }
        return true;
    }

    public void saveUser(String username) {
        System.out.println("Saving user: " + username);
        // Database logic would go here
    }
}
