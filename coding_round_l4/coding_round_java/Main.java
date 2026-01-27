class Main {

    // Candidate writes ONLY this method
    // input is ALWAYS a STRING
    public static Object solve(String input) {

        int num = 0;

        // Convert input string to integer manually
        for (int i = 0; i < input.length(); i++) {
            num = num * 10 + (input.charAt(i) - '0');
        }

        // Reverse the number
        int rev = 0;
        while (num > 0) {
            int digit = num % 10;
            rev = rev * 10 + digit;
            num /= 10;
        }

        return rev;
    }

    // ⚠️ DO NOT EDIT
    public static void main(String[] args) {
        if (args.length == 0) return;
        System.out.print(solve(args[0]));
    }
}
