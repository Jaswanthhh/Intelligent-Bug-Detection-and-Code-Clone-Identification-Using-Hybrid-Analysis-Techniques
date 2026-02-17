package com.example.samples;

import java.util.HashMap;
import java.util.Map;

/**
 * Another sample Java class for BCI testing
 * Demonstrates different programming patterns
 */
public class SampleJava2 {
    private Map<String, Integer> dataMap;
    private int counter;

    public SampleJava2() {
        this.dataMap = new HashMap<>();
        this.counter = 0;
    }

    public void processData(String key, int value) {
        dataMap.put(key, value);
        counter++;
        System.out.println("Processed: " + key + " = " + value);
    }

    public int getValue(String key) {
        return dataMap.getOrDefault(key, -1);
    }

    public boolean containsKey(String key) {
        return dataMap.containsKey(key);
    }

    public int getCounter() {
        return counter;
    }

    public void reset() {
        dataMap.clear();
        counter = 0;
        System.out.println("Data reset completed");
    }

    public void displayAll() {
        System.out.println("Current data:");
        for (Map.Entry<String, Integer> entry : dataMap.entrySet()) {
            System.out.println("  " + entry.getKey() + ": " + entry.getValue());
        }
    }

    public static void main(String[] args) {
        System.out.println("Starting SampleJava2 execution...");

        SampleJava2 sample = new SampleJava2();

        // Process some data
        sample.processData("apple", 5);
        sample.processData("banana", 3);
        sample.processData("cherry", 8);

        // Display results
        sample.displayAll();

        // Test lookups
        System.out.println("Value for 'apple': " + sample.getValue("apple"));
        System.out.println("Contains 'grape': " + sample.containsKey("grape"));
        System.out.println("Total processed: " + sample.getCounter());

        // Reset and test
        sample.reset();
        System.out.println("After reset - Counter: " + sample.getCounter());

        System.out.println("SampleJava2 execution completed.");
    }
}
