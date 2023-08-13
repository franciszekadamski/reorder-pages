#!/usr/bin/python3

from PyPDF2 import PdfReader, PdfWriter, PdfMerger, Transformation, PageObject
import copy
import os
import shutil
import argparse

def map_pages(P):
    T = {
            9 : 0,
            10 : 1,
            11 : 2,
            8 : 3,
            7 : 4,
            12 : 5,
            13 : 6,
            6 : 7,
            5 : 8,
            14 : 9,
            15 : 10,
            4 : 11,
            3 : 12,
            16 : 13,
            17 : 14,
            2 : 15,
            1 : 16,
            18 : 17,
            19 : 18,
            0 : 19    
        }
        
    data = [0 for _ in range(P)]
    pages = []
    for p in range(P):
        f = p  // 20
        r = p - 20*f                     
        new_p = 20*f + T[r]
        data[new_p] = p + 1

    for idx in range(0, len(data), 2):
        pages.append([data[idx], data[idx + 1]])

    pages_map = {(idx + 1) : element for idx, element in enumerate(pages)}
    print(pages_map)
    return pages_map
    
# test = map_pages(380)
# [ print(key, " => ", test[key]) for key in test ]

def extend_pages(src_path):
    dst_path = src_path.replace(".pdf", "_extended.pdf")
    pdf_reader = PdfReader(src_path)
    pdf_writer = PdfWriter()

    width = pdf_reader.pages[1].mediabox.width
    height = pdf_reader.pages[1].mediabox.height / 2

    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    for _ in range(40):
        pdf_writer.add_blank_page(width=width, height=height)

    pdf_writer.write(dst_path)
    
    return dst_path
    
def reorder_pages(src_path):
    dst_path = src_path.replace(".pdf", "_reordered.pdf")
    pdf_reader = PdfReader(src_path)
    pdf_writer = PdfWriter()

    width = pdf_reader.pages[1].mediabox.width
    height = pdf_reader.pages[1].mediabox.height / 2

    output_len = int((len(pdf_reader.pages)  - len(pdf_reader.pages) % 20)/2)

    pages_map = map_pages(output_len * 2)
    for page_number in range(1, output_len + 1):
        print(f"Processing page number {page_number} of {output_len + 1} pages")
        subpages = []
        for new_page_number in pages_map[page_number]:
            subpage = copy.deepcopy(pdf_reader.pages[int(new_page_number - 1)])
            subpages.append(subpage)

        page = PageObject().create_blank_page(width=width, height=height)
        
        subpage_1 = copy.deepcopy(subpages[0])
        subpage_2 = copy.deepcopy(subpages[1])
        
        subpage_1.add_transformation(Transformation().scale(0.5))
        subpage_2.add_transformation(Transformation().scale(0.5).translate(int(width//2), 0))

        page.merge_page(subpage_1)
        page.merge_page(subpage_2)
        
        pdf_writer.add_page(page)

    pdf_writer.write(dst_path)

    return dst_path

def divide_file_to_chunks(filename):
    pdf_reader = PdfReader(filename)
    number_of_pages = len(pdf_reader.pages)
    for page_number in range(0, number_of_pages, 10):
        pdf_writer = PdfWriter()
        for subnumber in range(10):
            pdf_writer.add_page(pdf_reader.pages[page_number + subnumber])

        new_filename = filename.replace(".pdf", f"_chunk_{int(page_number/10)}.pdf")
        pdf_writer.write(new_filename)
        print("Chunk ", int(page_number/10))
        
    print("Successfully written chunks")

def move_files_to_directory(key_name):
    filenames = os.listdir()
    try:
        os.mkdir(key_name)
    except:
        print(f"Directory {key_name} already exists")
        pass
    chunks_path = os.path.join(key_name, f"{key_name}_chunks")
    os.mkdir(chunks_path)
    for filename in filenames:
        if key_name in filename and "chunk" in filename:
            dst_path = os.path.join(chunks_path, filename)
            shutil.move(filename, dst_path)
            print(f"Moved file {filename} to folder {chunks_path}")
        elif key_name in filename:
            dst_path = os.path.join(key_name, filename)
            shutil.move(filename, dst_path)
            print(f"Moved file {filename} to folder {key_name}")

def main(filename="MAIN.pdf"):
    key_name = filename.replace(".pdf", "")
    
    src_path = extend_pages(filename)
    src_path = reorder_pages(src_path)
    divide_file_to_chunks(f"{key_name}_extended_reordered.pdf")

    move_files_to_directory(key_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    main(args.filename)