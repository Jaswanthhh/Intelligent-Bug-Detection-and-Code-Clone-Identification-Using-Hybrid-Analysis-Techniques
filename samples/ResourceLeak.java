import java.io.FileInputStream;
import java.io.IOException;

public class ResourceLeak {
    public void readFile(String path) throws IOException {
        // MEDIUM: Resource leak (stream not closed)
        FileInputStream fis = new FileInputStream(path);
        int data = fis.read();
        System.out.println(data);
        // fis.close() is missing
    }

    public boolean compare(String a, String b) {
        // MEDIUM: String comparison using ==
        return a == b;
    }
}
