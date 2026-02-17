#include <algorithm>
#include <iostream>
#include <vector>


void sortArray(std::vector<int> &data) {
  // Clone of bubbleSort logic (though implemented slightly differently)
  int len = data.size();
  bool swapped;
  for (int i = 0; i < len - 1; i++) {
    swapped = false;
    for (int j = 0; j < len - i - 1; j++) {
      if (data[j] > data[j + 1]) {
        int temp = data[j];
        data[j] = data[j + 1];
        data[j + 1] = temp;
        swapped = true;
      }
    }
    if (!swapped)
      break;
  }
}

int findElement(const std::vector<int> &list, int key) {
  // Clone of binarySearch
  int low = 0;
  int high = list.size() - 1;
  while (low <= high) {
    int mid = low + (high - low) / 2;
    if (list[mid] == key)
      return mid;
    if (list[mid] < key)
      low = mid + 1;
    else
      high = mid - 1;
  }
  return -1;
}
