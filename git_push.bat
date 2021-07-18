cd C:\Users\yizewang\Codes\AutoBladed\

call conda activate python3_6

pip freeze > requirements.txt

git add .

set /p message="Input log information: "
git commit -m "%message%"

git push origin HEAD:main

