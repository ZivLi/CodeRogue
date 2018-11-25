package main

import (
	"fmt"
	"math"
)

type Rectangle struct {
	width, heigth float64
}

type Circle struct {
	radius float64
}

func (r Rectangle) area() float64 {
	return r.width * r.heigth
}

func (c Circle) area() float64 {
	return c.radius * c.radius * math.Pi
}

func main(){
	r1 := Rectangle{12, 2}
	r2 := Circle{9}
	fmt.Println("Area 1: ", r1.area())
	fmt.Println("Area 2: ", r2.area())
}