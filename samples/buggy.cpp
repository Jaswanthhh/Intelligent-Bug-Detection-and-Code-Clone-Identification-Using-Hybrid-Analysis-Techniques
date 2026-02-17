#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void vulnerable_function(char *input) {
    char buffer[10];
    // BUG: Buffer overflow vulnerability
    strcpy(buffer, input);
    printf("Buffer content: %s\n", buffer);
}

int main() {
    char *secret = "SuperSecretPassword";
    
    // BUG: Memory leak (malloc without free)
    char *leak = (char *)malloc(100);
    strcpy(leak, "This memory will leak");
    
    // BUG: Use of system()
    system("ls -la");
    
    // BUG: Goto usage
    goto label;
    printf("Skipped\n");
    
label:
    printf("Jumped here\n");
    
    // BUG: Hardcoded credentials
    char *api_key = "12345-ABCDE";
    
    return 0;
}
