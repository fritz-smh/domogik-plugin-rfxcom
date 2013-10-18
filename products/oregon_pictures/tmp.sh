URL1="http://ftpserver.distec.be/OregonScientific/product_pictures/full/"

TMP_LIST=tmp/liste.tmp

rm -f $TMP_LIST
wget -O $TMP_LIST $URL1

#cat $TMP_LIST | grep "\[IMG\]" | sed -e 's/^.*([a-zA-Z]+[0-9]+\.jpg).*$/\\1/'
#cat $TMP_LIST | grep "\[IMG\]" | sed -e 's/[a-zA-Z_]*[0-9]*.jpg/XXXXXXXX/'
cat $TMP_LIST | grep "\[IMG\]" | grep -v "%20" | sed -e 's/^.*>\([a-zA-Z0-9_-]*\.jpg\).*$/\1/' | grep -v "<td>"
