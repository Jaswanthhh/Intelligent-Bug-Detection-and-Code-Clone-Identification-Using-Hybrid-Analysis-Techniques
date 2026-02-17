#include <iostream>

void unusedVariable() {
  // LOW: Unused variable
  int x = 10;
  std::cout << "Hello" << std::endl;
}

void magicNumber() {
  // LOW: Magic number
  for (int i = 0; i < 42; i++) {
    // ...
  }
}
