
set nocompatible
filetype off
set rtp+=~/.vim/bundle/Vundle.vim
"vim-go | go settings `go get -u github.com/golang/lint`
set rtp+=$GOPATH/src/github.com/golang/lint/misc/vim
call vundle#begin()
Plugin 'gmarik/Vundle.vim'                  "插件管理
Plugin 'yegappan/mru'                       "文件跳转
Plugin 'kchmck/vim-coffee-script'           "Coffee-script语法高亮
Plugin 'vim-scripts/mako.vim'               "mako语法高亮
Plugin 'scrooloose/syntastic'               "语法检查
Plugin 'vim-scripts/ctags.vim'              "生成Tag，跟TagList搭配
Plugin 'vim-scripts/taglist.vim'            "显示Tag
Plugin 'scrooloose/nerdtree'                "文件浏览
Plugin 'kien/ctrlp.vim'                     "根据文件名和文件内容模糊搜索并打开文件
"Plugin 'altercation/vim-colors-solarized'   "配色方案
Plugin 'bling/vim-airline'                  "底部状态栏
Plugin 'rking/ag.vim'                       "ag插件
Plugin 'dyng/ctrlsf.vim'                    "让ag支持上下文
Plugin 'ludovicchabant/vim-lawrencium'      "hg插件
Plugin 'jlfwong/vim-mercenary'              "hg插件，支持blame和diff
Plugin 'mattn/emmet-vim'                    "zen-codeing
Plugin 'luochen1990/rainbow'                "彩虹括号，匹配的括号显示为同一颜色
Plugin 'godlygeek/tabular'                  "自动对齐
Plugin 'tpope/vim-commentary'               "批量注释 
Plugin 'hynek/vim-python-pep8-indent'       "python自动缩进
Plugin 'edkolev/tmuxline.vim'               "Airline支持tmux
Plugin 'Valloric/YouCompleteMe'             "自动补全
Plugin 'wavded/vim-stylus'                  "plim
Plugin 'keitheis/vim-plim'                  "plim
Plugin 'tell-k/vim-autopep8'                "自动格式化
Plugin 'heavenshell/vim-pydocstring'        "自动生成python的docstring
Plugin 'ekalinin/Dockerfile.vim'            "Dockerfile
Plugin 'chase/vim-ansible-yaml'
" Plugin 'fholgado/minibufexpl.vim'           "打开文件的选项卡
" Plugin 'Yggdroot/indentLine'                "垂直缩进对齐线
" Plugin 'vim-scripts/matchit.zip'            "html标签跳转
Plugin 'gregsexton/MatchTag'                "html标签匹配高亮
" Plugin 'terryma/vim-multiple-cursors'       "多光标选择

call vundle#end()            " required
filetype plugin indent on    " required
"结束bundle

autocmd FileType python set commentstring=#\ %s
autocmd FileType html set commentstring=##\ %s
autocmd FileType coffee set commentstring=##\ %s
autocmd FileType sh set commentstring=#\ %s

"""""""""""""""""""""""""""""""""""""""
"
"            自定义函数
"
"""""""""""""""""""""""""""""""""""""""
" 打印选中行
function Rp() range
    exec "!sed -n " . a:firstline . "," . a:lastline . "p " . expand('%')
endfunction
"定义 RunSrc()
func RunPy2InPy3()
    call system("2to3-3.5 --fix=print --nobackups" . expand('%') . " -w &> /dev/null")
    exec ":e %"
    exec "!python %"
endfunc
"定义 RunSrc()
func RunSrc()
exec "w"
"运行python
if &filetype == 'py'||&filetype == 'python'
    "call RunPy2InPy3()
    exec "!python %"
endif
"使用zen-codeing补全html
if &filetype == 'html'
    call emmet#expandAbbr(3,"")
endif
if &filetype == 'sh'
    exec "!bash %"
endif
endfunc
"结束定义RunSrc  

"定义FormartSrc()
"需使用以下的格式化插件https://bitbucket.org/zuroc/42qu-linux-config
func FormartSrc()
exec "w"
if &filetype == 'c'
exec "!astyle --style=ansi --one-line=keep-statements -a --suffix=none %"
elseif &filetype == 'cpp' || &filetype == 'hpp'
exec "r !astyle --style=ansi --one-line=keep-statements -a --suffix=none %>
/dev/null 2>&1"
elseif &filetype == 'perl'
exec "!astyle --style=gnu --suffix=none %"
elseif &filetype == 'py'||&filetype == 'python'
exec "r !pydent % > /dev/null 2>&1"
elseif &filetype == 'java'
exec "!astyle --style=java --suffix=none %"
elseif &filetype == 'jsp'
exec "!astyle --style=gnu --suffix=none %"
elseif &filetype == 'xml'
exec "!astyle --style=gnu --suffix=none %"
endif
exec "e! %"
endfunc
"结束定义FormartSrc


"""""""""""""""""""""""""""""""""""""""
"
"            基本配置外观配置
"
"""""""""""""""""""""""""""""""""""""""
syntax on
syntax enable
set encoding=utf-8
set termencoding=utf-8
set fileencoding=utf-8
set nocompatible
set backspace=2
set number              "左侧显示行号
"set ruler               "底部显示行列号
set expandtab
set hlsearch            "搜索时匹配项高亮显示
"set autoindent          "新行自动缩进
set cindent             "C语言风格缩进
set showcmd             "命令行模式按tab补全命令
set wildmenu            "命令行模式按tab补全命令
set sw=4
set sts=4
"根据缩进折叠代码
set fdm=indent
filetype indent on
autocmd FileType python setlocal et sta sw=4 sts=4
autocmd FileType yaml setlocal et sta sw=2 sts=2
"python文件模板
if filereadable("~/.vim/py.tlp ")
    autocmd BufNewFile *.py  0r  ~/.vim/py.tlp
endif
retab 

"""""""""""""""""""""""""""""""""""""""
"            
"            ctrlp设置
"
"""""""""""""""""""""""""""""""""""""""
let g:ctrlp_custom_ignore = {
            \'file' : '\v\.(pyc|html\.py)$',
            \}


"""""""""""""""""""""""""""""""""""""""
"
"            nerdtree设置
"
"""""""""""""""""""""""""""""""""""""""
let NERDTreeIgnore=['\.pyc$', '\~$', '__pycache__$']
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif


"""""""""""""""""""""""""""""""""""""""
"        
"        Taglist and Ctags
"
"""""""""""""""""""""""""""""""""""""""
let Tlist_Show_One_File = 1 "不同时显示多个文件的tag，只显示当前文件的
let Tlist_Exit_OnlyWindow = 1 "如果taglist窗口是最后一个窗口，则退出vim
"let Tlist_Use_Right_Window = 1 "在右侧窗口中显示taglist窗口
let Tlist_File_Fold_Auto_Close = 1
"只显示当前文件tag，其它文件的tag都被折叠起来
"set tags=/andes/project/mkdemo/src/tags
set tags=tags;
"set autochdir
"F12生成/更新tags文件
"nmap <F12> :call UpdateTagsFile()<CR>
function! UpdateTagsFile()
silent !ctags -R --fields=+ianS --extra=+q
endfunction


"""""""""""""""""""""""""""""""""""""""
"               
"               airline            
"
"""""""""""""""""""""""""""""""""""""""
set laststatus=2
"let g:airline_powerline_fonts = 1
let g:airline#extensions#branch#enabled = 1
let g:airline#extensions#syntastic#enabled = 1
let g:airline#extensions#tabline#enabled = 1
let g:tmuxline_separators = {
    \ 'left' : '',
    \ 'left_alt': '>',
    \ 'right' : '',
    \ 'right_alt' : '<',
    \ 'space' : ' '}


"""""""""""""""""""""""""""""""""""""""
"
"            ycm setting
"
"""""""""""""""""""""""""""""""""""""""
let g:ycm_global_ycm_extra_conf = '/Users/ZivLi/.vim/bundle/YouCompleteMe/third_party/ycmd/cpp/ycm/.ycm_extra_conf.py'
let g:ycm_collect_identifiers_from_tags_files = 1
let g:ycm_seed_identifiers_with_syntax = 1
let g:ycm_autoclose_preview_window_after_insertion = 1
let g:ycm_autoclose_preview_window_after_completion = 1
let g:ycm_confirm_extra_conf = 0
let mapleader="\<Space>"
nnoremap <leader>gg :YcmCompleter GoToDefinitionElseDeclaration <CR>
"let g:ycm_server_keep_logfiles = 1     "写入日志文件
"let g:ycm_server_log_level = 'debug'       "打开调试模式
"""""""""""""""""""""""""""""""""""""""
"
"            autopep8自动格式化设置
"
"""""""""""""""""""""""""""""""""""""""
let g:autopep8_disable_show_diff=1

"""""""""""""""""""""""""""""""""""""""
"
"               颜色主题
"
"""""""""""""""""""""""""""""""""""""""
"let g:molokai_original = 1
"colorscheme molokai
"try
"syntax enable
"colorscheme solarized
"colorscheme corporation
"set background=dark
"set background=light
"let g:solarized_termcolors=256
"catch
"endtry
"let g:solarized_termtrans=1
""set cursorline                         "光标所在行高亮

highlight CursorLine ctermbg=240 cterm=bold
let g:rainbow_active = 1    "彩虹括号


"""""""""""""""""""""""""""""""""""""""
"
"            syntastic设置
"
"""""""""""""""""""""""""""""""""""""""
"let g:syntastic_mode_map = { 'mode': 'active', 'active_filetypes': [],'passive_filetypes': ['html'] }
let g:syntastic_always_populate_loc_list = 1
let g:syntastic_check_on_open = 1
let g:syntastic_error_symbol = '✗'
let g:syntastic_warning_symbol = '⚠'
let g:syntastic_html_tidy_ignore_errors=[" proprietary attribute \"ms_"]
"let g:syntastic_python_checkers = ['pyflakes']
let g:syntastic_python_checkers = ['flake8']
let g:syntastic_coffee_checkers = ['coffeelint']
let g:syntastic_coffee_coffeelint_args = "-f ~/.coffeelint.json"
highlight link SyntasticError ErrorMsg
" highlight link SyntasticWarning ErrorMsg
" highlight link SyntasticStyleError ErrorMsg
" highlight link SyntasticStyleWarning ErrorMsg

nnoremap <C-w>E :SyntasticCheck<CR> :SyntasticToggleMode<CR>


"""""""""""""""""""""""""""""""""""""""
"
"           解决长行文本变卡                
"
"""""""""""""""""""""""""""""""""""""""
"set synmaxcol=128
set ttyfast
set ttyscroll=3
set lazyredraw
"""""""""""""""""""""""""""""""""""""""
"
"               快捷键                 
"
"""""""""""""""""""""""""""""""""""""""
"解决组合快捷键导致某些快捷键变卡的问题
"例如如果map了np, 就会导致搜索n有一个很长的反应时间
set timeoutlen=200 
map <F12> :call RunSrc()<CR>
map <C-F11> :call Autopep8()<CR>
map <F11> :call Autopep8()<CR>
"map <F10> :SyntasticCheck pyflakes<CR>
map <F9> :SyntasticCheck python<CR>
map <F8> :res-1<CR>
map <F7> :res+1<CR>
map <F6> :vertical res-1<CR>
map <F5> :vertical res+1<CR>
map <F4> :call FormartSrc()<CR>
" map <F3> :set paste<CR>
" map <F2> :set nopaste<CR>
" 方便复制文件
vnoremap <F2> :call Rp() <CR>
"ag搜索
nmap <C-S>f :CtrlSF  
nmap <C-S>o :CtrlSFOpen<CR> 
nmap ss :CtrlSF <C-R><C-W><CR>
vnoremap ss y:CtrlSF <C-R>"<CR>
vnoremap <C-Tab> :Tabularize <C-R><C-W><CR>
vnoremap <Backspace> :Commentary <CR>

"nmap <C-N>t :NERDTree<cr>
map <F10> :NERDTree<CR>
nmap mr :MRU<cr>
nmap tl :TlistToggle<cr>
nmap bn :bn<cr>
nmap bp :bp<cr>
nmap ne :lnext<cr>
nmap pe :lprev<cr>

map <F2> <Esc>: call ToggleCopy()<CR>
let g:copymode=0
function ToggleCopy()
    if g:copymode
        set number
    else
        set nonumber
    endif
    let g:copymode=!g:copymode
endfunction
Plugin 'wakatime/vim-wakatime'

function! Zoom ()
    if tabpagenr('$') > 1 && tabpagewinnr(tabpagenr(), '$') == 1
        let l: cur_winview = winsaveview()
        let l: cur_bufname = bufname('')
        tabclose

        if l: cur_bufname == bufname('')
            call winrestview(cur_winview)
        endif
    else
        tab split
    endif
endfunction

nmap <leader>z :call Zoom()<CR>
