call .\build.bat

REM create output dir if it does not exist
if not exist %~dp0\output mkdir %~dp0\output

docker run --rm^
 --memory=16g^
 -v %~dp0\test\:/input/^
 -v %~dp0\output\:/output/^
 hanseg2023algorithm

echo
echo
echo "Compare files in %~dp0 with the expected results to see if test is successful"