public class t{
    public static void helper(int arr[])
    {
        System.out.println("First element is:" + " "+ arr[0]);
        System.out.println("Second element is:" + " "+ arr[1]);
    }
    public static void main(String args[])
    {
        System.out.println("Test webhook trigger for Github action");
        System.out.println(" webhook trigger for Github action");
        System.out.println("Latest trigger check");
        System.out.println("Latest trigge github check");
        System.out.println("Latest trigge github check after enriching using Rest APIS check ");
        System.out.println("final check");
    }
    public static int binSearch(int nums[], int targetElement)
    {
        int n=nums.length;
        int low=0, high=n-1;
        while(low <= high)
        {
            int mid = low + (high-low)/2;
            if(nums[mid]==targetElement)
            {
                return mid;
            }
            else if(nums[mid] < targetElement)
            {
                low++;
            }
            else
            {
                high--;
            }
        }
        return -1;
    }
    public static boolean linSearch(int nums[] , int target)
    {
        for(int val : nums)
        {
            if(val == target) return true;
        }
        return false;
    }
}