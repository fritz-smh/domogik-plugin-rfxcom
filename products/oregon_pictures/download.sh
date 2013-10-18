URL1="http://ftpserver.distec.be/OregonScientific/product_pictures/sensors/"
URL2="http://ftpserver.distec.be/OregonScientific/product_pictures/weather/"
URL3="http://ftpserver.distec.be/OregonScientific/product_pictures/full/"

TMP_DIR=./tmp/
MANUAL_DL_DIR=./manually_downloaded/
JSON_FILE=../../info.json
PRODUCT_DIR=../
TMP_LIST=$TMP_DIR/liste.tmp





# clean old data
mkdir -p $TMP_DIR
rm -f $TMP_DIR/*

for URL in $URL1 $URL2 $URL3
  do
    # get the pictures list
    echo "***** processing $URL *****"
    wget -O $TMP_LIST $URL > /dev/null 2>&1
    # the first grep keep only the lines with pictures in the html file
    # the second grep remove pictures with white spaces in the name
    # the sed will keep only file names from html code
    # the next grep -v filters for non processed pictures (by the sed)
    # the next grep -v avoir to get _01, _02, ... pictures which are other views of the original one
    # the next one will avoir to use all the solar models pictures
    # the next one will skip the black models
    list=$(cat $TMP_LIST | grep "\[IMG\]" | grep -v "%20" | sed -e 's/^.*>\([a-zA-Z0-9_-]*\.jpg\).*$/\1/' | grep -v "<td>" | grep -v "_[0-9][0-9]\." | grep -v "ES\." | grep -v "NF\.")



    # download all the pictures
    for file in $list
      do
        lower_file="$(tr [A-Z] [a-z] <<< "$file")"
        id=$(echo $lower_file | sed "s/[a-z]*.jpg//")
        final_filename=$(grep $id $JSON_FILE | sed "s/^.* : \"//" | sed "s/\", *$//")
        # skip files not found in the json
        echo $final_filename
        if [ X$final_filename != "X" ] ; then
            echo $final_filename
            wget -O $TMP_DIR/${final_filename}.jpg $URL/$file > /dev/null 2>&1
        fi
    done
done


# copy all the files where they should be
cp $TMP_DIR/* $PRODUCT_DIR/
cp $MANUAL_DL_DIR/* $PRODUCT_DIR/
