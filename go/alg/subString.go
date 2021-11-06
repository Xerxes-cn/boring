package alg

func LengthOfLongestSubstring(s string) int {
	length := len(s)
	ans := 0
	cmap := make([]int, 128)
	left := 0
	for right := 0; right < length; right ++ {
		idx := s[right]
		left := max(left, cmap[idx])
		ans = max(ans, right-left+1)
		cmap[idx] = right + 1
	}
	return ans
}

func max(x, y int) int{
	if x < y {
		return y
	}
	return x
}
