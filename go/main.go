package main

import (
	"fmt"
)


func main()  {
	s := "345"
	fmt.Println(LetterCombinations(s))
}

var phoneMap = map[string]string{
	"2": "abc",
	"3": "def",
	"4": "ghi",
	"5": "jkl",
	"6": "mno",
	"7": "pqrs",
	"8": "tuv",
	"9": "wxyz",
}

var combinations []string

func LetterCombinations(digits string) []string {
	if len(digits) == 0 {
		return []string{}
	}
	combinations = []string{}
	BackTrack(digits, 0, "")
	return combinations

}

func BackTrack(digits string, index int, combination string) {
	if len(digits) == index {
		combinations = append(combinations, combination)
	} else {
		digit := string(digits[index])
		letters := phoneMap[digit]
		lettersCount := len(letters)
		for i := 0; i < lettersCount; i++ {
			BackTrack(digits, index + 1, combination + string(letters[i]))
		}
	}
}