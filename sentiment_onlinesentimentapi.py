from suds.xsd.doctor import Import, ImportDoctor
from suds.client import Client
import pickle
import time
import logging
logging.getLogger('suds.client').setLevel(logging.CRITICAL)

# -------------------------------------------------------------------------------------------------------------------------
# fix broken wsdl
# add <s:import namespace="http://www.w3.org/2001/XMLSchema"/> to the wsdl
imp = Import('http://www.w3.org/2001/XMLSchema',
             location='http://www.w3.org/2001/XMLSchema.xsd')
imp.filter.add('http://tempuri.org/')
wsdl_url = 'http://api.sentimentanalysisonline.com/sentimentscore.asmx?wsdl'
client = Client(wsdl_url, doctor=ImportDoctor(imp))
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Load Bloomberg Data
with open('AssetIds_200k_Stemmed.txt', 'rb') as fassets:
    assetids = pickle.load(fassets) 
    #assetids = assetids[:1000] 
print "Asset IDs loaded."
with open('ShelfLife_200k_Stemmed.txt', 'rb') as fslife:
    slife = pickle.load(fslife)
print "ShelfLife loaded."
with open('Corpus_200k_ActualText.txt', 'rb') as fcorpus:    
    #Corpus_Headlines_200k
    corpus = pickle.load(fcorpus)
print "Corpus loaded."
print "Length of corpus ", len(corpus)
with open('Hits_200k_Stemmed_New.txt', 'rb') as fhits:
    #Corpus_Headlines_200k
    hits = pickle.load(fhits)
print "Hits loaded."
with open('Corpus_HeadlinesNew.txt', 'rb') as ftitle:
    #Corpus_Headlines_200k
    titles = pickle.load(ftitle)
print "Titles loaded."
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# Open and maintain csv for score data
fd = open('sentiment_output.csv', 'a')
print "Sentiment CSV output open"
# -------------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------------
# API Information - http://www.sentimentanalysisonline.com/page/documentation/
key = "zbfv9949ZBzbfvZB"  # api key
# -------------------------------------------------------------------------------------------------------------------------
# make request
# Ranges run to date: 0 to 5, 
start = 1761
stop = 1775

# sentiment_array is an array of array (sentiment_row)
sentiment_array = []
# array: asset id | title | hits | shelf life | sentiment score
sentiment_row = []

outer_1 =  "<?xml version='1.0'?><root><apikey>zbfv9949ZBzbfvZB</apikey><QueryItems>"
outer_2 = "</QueryItems></root>"
i1 = "<query><id>"
i2 = "</id><brandname>"
i3 = "</brandname><paragraph>"
i4 = "</paragraph></query>"

query_form = []

for i in range(start, stop):
    id = assetids[i]
    title = titles[i]
    article = str(corpus[i])
    article = article[50:200]
    article = article.replace("\t", " ").replace("\n", " ")
    input_data_inner=str(i1+id+i2+title+i3+article+i4)
    query_form.append(input_data_inner)
    del id,title,article

inside = ""
for j in query_form:
    inside = inside + j

    
print "api initialized"
input_data = str((outer_1 + inside + outer_2))
#print input_data
  
result = client.service.GetScore(input_data)
result = result.replace("<?xml version=\"1.0\"?><root>","").replace("</id>", "").replace("</result>", " ").replace("</root>","")
exploded_result = result.split()

export_array = []
row_arr = []
counter = start
for row in exploded_result:
    t = row.replace('<id>', '').replace('<replace>', ' ').replace('<result>', ' ')
    #t = t.split()
    row_arr.append(assetids[counter])
    #row_arr.append(titles[counter])
    row_arr.append(slife[counter])
    row_arr.append(hits[counter])
    row_arr.append(t)
    #row_arr.append(t[1])
    export_array.append(row_arr[:])
    counter += 1
    del row_arr[:]
    del t

print "length of export array: ", len(export_array)
for k in range(0, len(export_array)):
    k = str(export_array[k][:])+'\n'
    fd.write(k)

print "END"


# -------------------------------------------------------------------------------------------------------------------------
