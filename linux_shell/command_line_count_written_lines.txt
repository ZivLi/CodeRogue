find . -name "*.py" -exec grep -Ev "^$" {} \; | wc -l
