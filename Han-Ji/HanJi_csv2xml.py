import re
import pandas as pd
import argparse
from lxml import etree

def HanJi_csv2xml(df_head, df_passage):
    # construct root element
    root = etree.Element("lg", type="poem")

    # construct header and author
    author = etree.SubElement(root, "author")
    author.text = "".join([a for a in df_head.author if type(a) == str])
    head = etree.SubElement(root, "head")
    for header, comment in zip(df_head.passage, df_head.comment):
        # add a child element, head, for our XML
        child_head = etree.SubElement(head, "l")
        child_head.text = header.replace("\u3000", "")

        # add a child element, comment in head, for our XML
        if type(comment) == str:
            child_head_comment = etree.SubElement(child_head, "comment")
            child_head_comment.text = comment 

    # construct main text 
    for passage, comment in zip(df_passage.passage, df_passage.comment):
        # add a child element, passage, for our XML
        child_passage = etree.SubElement(root, "l")
        child_passage.text = passage

        # add a child element, comment, for our XML
        child_child_comment = etree.SubElement(child_passage, "comment")
        child_child_comment.text = comment if type(comment) == str else ""
        
    return root


def main(args):
    
    filename_passage = args.filename_passage
    
    # use re to scrpate the name of this poem    
    filename_head = re.sub(r"_(.*?)_", r'_Head_', filename_passage)
    filename_XML  = re.sub(r".csv", r'.xml', filename_passage)

    # loading DataFrames
    df_passage = pd.read_csv(filename_passage)
    df_head    = pd.read_csv(filename_head)
    
    # create etree elemets from csv2xml function
    root = HanJi_csv2xml(df_head, df_passage)

    # writing xml file
    with open(filename_XML, "w", encoding="utf-8") as file:
        file.write(
            etree.tostring(root, encoding="unicode", pretty_print=True), 
        )
        
if __name__ == "__main__":
    # argument parser, building flags
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename_passage', type=str, 
                        help='The filename of passage for Han-ji csv you want to convert to xml.')
    args = parser.parse_args()                        
    
    main(args)