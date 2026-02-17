package com.example.samples;

import java.util.ArrayList;
import java.util.List;

/**
 * Sample Java class for BCI testing
 * Demonstrates basic object-oriented programming patterns
 */
public class SampleJava1 {
    private String name;
    private List<Integer> numbers;

    public SampleJava1(String name) {
        this.name = name;
        this.numbers = new ArrayList<>();
    }

    public void addNumber(int number) {
        numbers.add(number);
        System.out.println("Added number: " + number);
    }

    public int calculateSum() {
        int sum = 0;
        for (int num : numbers) {
            sum += num;
        }
        return sum;
    }

    public double calculateAverage() {
        if (numbers.isEmpty()) {
            return 0.0;
        }
        return (double) calculateSum() / numbers.size();
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public static void main(String[] args) {
        System.out.println("Starting SampleJava1 execution...");

        SampleJava1 sample = new SampleJava1("TestSample");

        // Add some numbers
        sample.addNumber(10);
        sample.addNumber(20);
        sample.addNumber(30);

        // Calculate and display results
        int sum = sample.calculateSum();
        double avg = sample.calculateAverage();

        System.out.println("Sum: " + sum);
        System.out.println("Average: " + avg);
        System.out.println("Name: " + sample.getName());

        System.out.println("SampleJava1 execution completed.");
    }
}
