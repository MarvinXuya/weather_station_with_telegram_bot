pais=$1
if [ -z $pais ] ; then
  exit 1
fi
data=$(curl -s https://www.bing.com/covid/local/${pais})

echo $data | sed 's/^.*data={"id"/{"id"/'| awk -F ";</script></div></body></html>" '{print $1}' | jq -r '.areas|.[]| select(.id=="guatemala")|del(.areas)'
