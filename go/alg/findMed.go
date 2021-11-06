package alg


func FindMedianSortedArrays(nums1 []int, nums2 []int) float64 {
	totalLength := len(nums1) + len(nums2)
	if totalLength % 2 == 1{
		midIdx := totalLength/2
		return float64(getKthElement(nums1, nums2, midIdx + 1))
	}else{
		minIdx1, minIdx2 := totalLength/2 -1, totalLength/2
		return float64(getKthElement(nums1, nums2, minIdx1 + 1) + getKthElement(nums1, nums2, minIdx2 + 1)) / 2.0
	}
}

func getKthElement(nums1 []int, nums2 []int, k int) int {
	idx1, idx2 := 0, 0
	if len(nums1) == 0 && len(nums2) ==  0{
		return 0
	}
	for {
		if idx1 == len(nums1) {
			return nums1[idx2 + k - 1]
		}
		if idx2 == len(nums2) {
			return nums1[idx1 + k -1]
		}
		if k == 1 {
			return min(nums1[idx1], nums2[idx2])
		}
		half := k/2
		newIdx1 := min(idx1 + half, len(nums1)) - 1
		newIdx2 := min(idx2 + half, len(nums2)) - 1
		piv1, piv2 := nums1[newIdx1], nums2[newIdx2]
		if piv1 <= piv2{
			k -= (newIdx1 - idx1 + 1)
			idx1 = newIdx1 + 1
		} else {
			k -= (newIdx2 - idx2 + 1)
			idx2 = newIdx2 + 1
		}
	}
}

func min(x, y int) int {
	if x > y {
		return y
	}
	return x
}

func FindMedianSortedArraysV2(nums1, nums2 []int) float64 {
	i, j, k := 0, 0, 0
	pre, cur := 0, 0
	n1, n2 := len(nums1), len(nums2)
	m := n1 + n2
	mid := m / 2
	for k < mid {
		pre = cur
		if i < n1 && j < n2 {
			if nums1[i] < nums2[j]{
				cur = nums1[i]
				i++
			} else {
				cur = nums2[j]
				j++
			}
		} else if i < n1{
			cur = nums2[j]
			j++
		} else {
			cur = nums1[1]
			i++
		}
		k++
	}
	if m % 2 == 0 {
		return float64(pre + cur) / 2
	}
	return float64(cur)
}
