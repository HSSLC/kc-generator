import os, json, re, shutil, hashlib
from PIL import Image
size = lambda d:sum(os.stat(os.path.join(cd, f)).st_size for cd, sd, fs in os.walk(d) for f in fs if os.path.isfile(os.path.join(cd, f)))
#init
os.chdir('frames')
with open('page_frame.html', 'r') as page_frame_file:
    page_frame = page_frame_file.read()
    #title
    #width
    #height
    #top
    #bottom
    #src
with open('content_frame.opf', 'r') as opf_frame_file:
    opf_frame = opf_frame_file.read()
    #uid
    #title
    #language
    #creator
    #direction
    #width
    #height
    #cover meta
    #cover src
    #manifest
    #spine
with open('opf_manifest_frame.xml', 'r') as omf_file:
    omf_frame = omf_file.read()
    #href
    #id
with open('itemref_frame.xml', 'r') as if_file:
    if_frame = if_file.read()
    #id
with open('toc_frame.ncx', 'r') as toc_frame_file:
    toc_frame = toc_frame_file.read()
    #navmap
with open('navmap_frame.xml', 'r') as navmap_frame_file:
    navmap_frame = navmap_frame_file.read()
    #playOrder
    #id
    #name
    #src
with open('cover_frame.xml', 'r') as cover_frame_file:
    cover_frame = cover_frame_file.read()
    #src
with open('cover_meta_frame.xml', 'r') as cover_meta_frame_file:
    cover_meta_frame = cover_meta_frame_file.read()
os.chdir('..')
program_dir = os.getcwd()

def main():
    def sort_lambda(n):
        try:
            return float(re.search('(\d+(\.\d+)?)', n).group(0))
        except:
            return 0
    print('輸入工作目錄:', end='')
    os.chdir(input())
    try:
        with open('config.json', 'r', encoding='UTF-8') as config_json:
            conf = json.load(config_json)
    except:
        print('沒有config.json')
        return
    main_folder = title = creator = lang = None
    try:
        main_folder = conf['folder']
        title = conf['title']
        creator = conf['creator']
        lang = conf['language']
        h = int(conf['height'])
        w = int(conf['width'])
        cover = conf['cover']
        direction = conf['direction']
    except:
        print('config.json不完整')
        return
    
    book_hash = hashlib.md5(bytes(title + creator, encoding='UTF-8')).hexdigest()
    ch_folders = os.listdir(main_folder)
    ch_folders.sort(key=sort_lambda)
    #自訂章節排序
    print('是否要自訂排序:(y/n)')
    isusersort = input()
    if isusersort == 'y':
        with open('sort.txt', 'w', encoding='utf-8') as sortlist:
            sortlist.write('\n'.join(ch_folders))
        print('請檢查sort.txt並修改排序 請勿加入其他資訊避免錯誤')
        print('修改完存檔並按enter繼續')
        input()
        with open('sort.txt', encoding='utf-8') as sortlist:
            ch_folders = sortlist.read().split('\n')
    #章節排序
    if not os.path.exists('proj') or not os.path.isdir('proj'):
        os.mkdir('proj')
    if not cover == '':
        shutil.copyfile(cover, os.path.join('proj', cover))
    #進入proj目錄
    os.chdir('proj')
    if not os.path.exists('html') or not os.path.isdir('html'):
        os.mkdir('html')
    os.chdir('html')
    if not os.path.exists('img') or not os.path.isdir('img'):
        os.mkdir('img')
    #返回工作目錄
    os.chdir('..')
    toc = open('toc.ncx', 'w', encoding='UTF-8')
    opf = open('content.opf', 'w', encoding='UTF-8')
    work_dir = os.getcwd()
    os.chdir('..')
    manifest = []
    spine = []
    navmap = []
    os.chdir(main_folder)
    page_count = 1
    print('正在創建檔案...')
    for ch in ch_folders:
        #run each chapter
        if not os.path.isdir(ch):
            continue
        print(ch)
        page_files = os.listdir(ch)
        #頁面排序
        page_files.sort(key=sort_lambda)
        os.chdir(ch)
        navmap.append(navmap_frame % (page_count, page_count, ch, 'html/Page-%s.html' % page_count))
        for page in page_files:
            #run each page
            if not os.path.isfile(page) or not page.endswith('.jpg'):
                continue
            try:
                im = Image.open(page)
            except:
                print('檔案錯誤: %s 已略過' % page)
                continue
            width, height = im.size
            scale = w / width
            adjh = int(height * scale)
            margin_sky_and_ground = int((h - adjh) / 2)
            #copy page image
            shutil.copyfile(page, os.path.join('..', '..','proj', 'html', 'img', '%s.jpg' % page_count))
            with open(os.path.join('..', '..','proj', 'html', 'Page-%s.html' % page_count), 'w', encoding='UTF-8') as page_html:
                page_html.write(page_frame % (page_count, w, adjh, margin_sky_and_ground, margin_sky_and_ground, '/'.join(['img', '%s.jpg' % page_count])))
            manifest.append(omf_frame % ('html/Page-%s.html' % page_count, str(page_count + 2)))
            spine.append(if_frame % str(page_count + 2))
            page_count += 1
        os.chdir('..')
    if not cover == '':
        cover_xml = cover_frame % cover
        cover_meta_xml = cover_meta_frame
    else:
        cover_xml = ''
        cover_meta_xml = ''
    opf.write(opf_frame % (book_hash, title, lang, creator, direction, w, h, cover_meta_xml, cover_xml, '\n\t\t'.join(manifest), '\n\t\t'.join(spine)))
    opf.close()
    toc.write(toc_frame % '\n'.join(navmap))
    toc.close()
    os.chdir(os.path.join('..', 'proj'))
    #呼叫kindlegen
    print('呼叫kindlegen...')
    output_name = re.sub(r'[\\/:*?"<>|]', '_', title) + '.mobi'
    os.system('""%s" -dont_append_source -verbose -locale en -o "%s" "%s""' % (os.path.join(program_dir, 'kindlegen.exe'), output_name, os.path.join(work_dir, 'content.opf')))
    #把輸出檔案向上移一層
    src_file = os.path.join('..', output_name)
    if os.path.exists(src_file) and os.path.isfile(src_file):
        os.remove(src_file)
    os.rename(output_name, src_file)
main()
