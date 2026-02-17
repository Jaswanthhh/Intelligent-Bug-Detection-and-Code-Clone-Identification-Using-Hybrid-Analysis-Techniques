public class AdminManager {
    // This method is a clone of validateUser in UserManager
    public boolean checkAdmin(String adminName, String adminPass) {
        if (adminName == null || adminName.length() == 0) {
            return false;
        }
        if (adminPass == null || adminPass.length() < 8) {
            return false;
        }
        return true;
    }

    public void persistAdmin(String name) {
        System.out.println("Persisting admin: " + name);
        // DB save logic
    }
}
