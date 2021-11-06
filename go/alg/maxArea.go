package alg


func MaxArea(height []int) int {
	n := len(height)
	if n <= 1 {
		return 0
	}
	area := 0
	start, end := 0, n -1
	for start < end {
		x := height[start]
		y := height[end]
		area = GetMax(area, (end-start) * GetMin(x, y))
		if x > y {
			end -= 1
		}else {
			start +=1
		}
	}
	return area
}

func GetMin(x, y int) int {
	if x < y {
		return x
	}
	return y
}

func GetMax(x, y int) int {
	if x > y {
		return x
	}
	return y
}