package alg

func LongestPalindrome(s string) string {
	n := len(s)
	if n < 2 {
		return s
	}
	start, end := 0, 0
	for i := 0; i < n; i++{
		l1, r1 := ExpandAroundCenter(s, i, i)
		l2, r2 := ExpandAroundCenter(s, i, i+1)
		if r1 - l1 > end - start{
			end, start = r1, l1
		}
		if r2 - l2 > end - start{
			end, start = r2, l2
		}
	}
	return s[start: end+1]
}

func ExpandAroundCenter(s string, l, r int) (left, right int) {
	for ; l >= 0 && r < len(s) && s[l] == s[r]; l, r = l-1, r+1 { }
	return l + 1,  r - 1
}