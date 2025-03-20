\LoadClass{article}

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ledger}

\RequirePackage{titlesec}
\RequirePackage[superscript,biblabel]{cite}
\RequirePackage{subfig}
\RequirePackage{numprint}
\npthousandsep{,}\npthousandthpartsep{}\npdecimalsign{.}
\newcommand{\num}[1]{\numprint{#1}}
\newcommand{\q}[2]{\num{#1}~{#2}}
\newcommand{\percent}[1]{\num{#1}\%}

% Use fontspec for custom fonts (requires XeLaTeX or LuaLaTeX)
\RequirePackage{fontspec}
\RequirePackage[english,russian]{babel}
\usepackage{graphicx}
\usepackage{indentfirst}
\usepackage{ulem}

% Set Times New Roman as the font for both English and Russian
\setmainfont{Times New Roman} % For English text
\newfontfamily\russianfont{Times New Roman} % For Russian text
\newfontfamily\cyrillicfont{Times New Roman} % For Cyrillic symbols in math

% Math and general formatting
\RequirePackage{amsmath,amssymb}
\RequirePackage{microtype}

% Header and margins
\setlength{\headheight}{34pt}
\newlength{\topmarginheight}
\setlength{\topmarginheight}{2.4cm}
\newlength{\headersep}
\setlength{\headersep}{\topmarginheight}
\addtolength{\headersep}{-\headheight}
\addtolength{\headersep}{-1.5cm}
\RequirePackage[left=3.1cm,right=3.1cm,top=\topmarginheight,bottom=1cm,headsep=\headersep,includefoot]{geometry}

% Graphics and colors
\graphicspath{{./images/}}
\RequirePackage{pbox}
\RequirePackage{framed}
\RequirePackage{color}
\RequirePackage{fancyhdr}
\renewcommand{\headrulewidth}{0pt}

% Hyperlinks
\RequirePackage[pdfpagelabels, hidelinks,
  bookmarks=false, unicode=true, pageanchor=false,
  pdfproducer={Latex with hyperref},
  pdfcreator={pdflatex}]{hyperref}

\RequirePackage{breakurl}

\AtBeginDocument{\urlstyle{pcr}}

\fancypagestyle{pagefirst}{%

  \lhead{\includegraphics[height=1cm]{1}}%

}

\fancypagestyle{pagemain}{%
  \fancyhf{}%

  \cfoot{\raisebox{0.25cm-\height}{\textbf{\thepage}}}
      \lfoot{\raisebox{0.5cm-\height}} 

}

\fancypagestyle{pagelast}{%
  \fancyhf{}%

  \chead{\raisebox{1cm-\height}{LEDGER VOL \thevol~(\theyear) \ledgerpages}}

  \cfoot{\raisebox{0.25cm-\height}{\textbf{\thepage}}
    \begin{minipage}[t]{\textwidth}
    {\vspace*{-5cm}\centering\includegraphics[width=\textwidth]{logoCreativeCommons}}%
    \end{minipage}
  }
  
  \lfoot{\raisebox{0.5cm-\height}{\includegraphics[height=0.3cm]{logoSmall}}}%
  \rfoot{\raisebox{0.5cm-\height}
    {\begin{minipage}[t]{.48\textwidth}
      \begin{flushright}
      \fontsize{8pt}{8pt}\selectfont \sffamily\color{gray}SSN 2379-5980 (online)
      \\ \thedoi
      \end{flushright}
    \end{minipage}}}
}

\RequirePackage{caption} % Allows customization of captions

\RequirePackage{cleveref} % Used for 'smart' references


\RequirePackage{fnpct} % Change default footnote/punctuation behavior

\RequirePackage[inline]{enumitem} % Allows inline lists.  Used for keywords.
\setlist{leftmargin=1.2cm,labelindent*=.6cm,itemsep=0cm,parsep=0cm,topsep=0cm}
\setlist[enumerate]{label=(\arabic*)}
\setlist[description]{labelindent=\parindent-0.5em}


\RequirePackage{endnotes} % Used for making endnotes

\RequirePackage{listings} % Code
\lstset{breaklines=true,basicstyle=\ttfamily\fontsize{10pt}{11pt}\selectfont,xleftmargin=1.2cm,breakindent=.6cm}


\newcommand{\blankline}{\vspace{\baselineskip}} % Adds a blank line

% Stores the length of a single space
\newlength{\spacelength}
\settowidth{\spacelength}{\ }

% FORMATTING

\setlength{\parskip}{0pt} % So that we know exactly how much space goes between
                          % different elements

% This gets rid of extra vertical spacing in the center environment
\let\oldcenter\center
\let\oldendcenter\endcenter
\renewenvironment{center}{%
  \setlength\topsep{0pt}
  \setlength\parskip{0pt}
  \oldcenter
}{%
  \oldendcenter
}



% Centers footnotes
\renewcommand{\footnoterule}{\noindent\hfil\rule{0.75\textwidth}{0.6pt}\hfil}


% Title and authors

\RequirePackage{titling} % Allows customization of \maketitle

\renewcommand{\and}{,\ } % Command goes between author names
\renewcommand{\thanks}[1]{\footnote{\centering \fontsize{8pt}{9pt}\selectfont
    #1\vspace{1pt}}\thanksgap{\spacelength}}

\predate{} % Removes date
\date{}
\postdate{}

% Abstract

% Определяем отступы для аннотации
\newlength{\abstractleftmargin}
\newlength{\abstractrightmargin}
\setlength{\abstractleftmargin}{1.2cm} % Отступ слева
\setlength{\abstractrightmargin}{0.06cm} % Отступ справа

% Определяем ширину аннотации на основе отступов
\newlength{\abstractwidth}
\setlength{\abstractwidth}{\textwidth}
\addtolength{\abstractwidth}{-\abstractleftmargin}
\addtolength{\abstractwidth}{-\abstractrightmargin}

% Определяем аннотацию на русском с настраиваемыми отступами
\renewenvironment{abstract}{%

    \noindent\hspace*{\abstractleftmargin} % Отступ слева
    \begin{minipage}{\abstractwidth}%
        \fontsize{10pt}{13pt}\selectfont \normalfont \textbf{Резюме.}%
    }{%
    \end{minipage}%

    \par%
}


% Body

\renewcommand{\baselinestretch}{1.13}


% Keywords

\let\olditem\item
\renewcommand{\item}[1]{\olditem \mbox{#1}}
\newlength{\keywordsmargins}
\setlength{\keywordsmargins}{1cm}
\newlength{\keywordswidth}
\setlength{\keywordswidth}{\textwidth}
\addtolength{\keywordswidth}{-2\keywordsmargins}
\newenvironment{keywords}{\vspace{9pt}
    {\centering\fontsize{10pt}{13pt}\selectfont\textsc{КЛЮЧЕВЫЕ СЛОВА}\par}\vspace{6pt}
    \begin{center}\begin{minipage}{\keywordswidth}\begin{center}\begin{enumerate*}[itemjoin={\hspace{1em}},label=\arabic*.]}{\end{enumerate*}\end{center}\end{minipage}\end{center}}

% Section and subsection

\RequirePackage{titlesec} % Allows customization of \section

\titleformat{\section}{\fontsize{13pt}{13pt}\normalfont\bfseries}{}{0em}{\thesection .\quad}
\titleformat{name=\section,numberless}{\fontsize{13pt}{13pt}\normalfont\bfseries}{}{0em}{}
\titlespacing*{\section}{0pt}{15pt}{7pt}

\def\ledgernotes{
    \titleformat{\section}{\fontsize{13pt}{13pt}\normalfont\bfseries}{}{0em}{}
    \titlespacing*{\section}{0pt}{15pt}{7pt}
}

% Mathematics

\setlength{\abovedisplayskip}{9pt}
\setlength{\abovedisplayshortskip}{9pt}
\setlength{\belowdisplayskip}{7pt}
\setlength{\belowdisplayshortskip}{7pt}

\RequirePackage{amsthm}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{corollary}{Corollary}[theorem]
\newtheorem{lemma}[theorem]{Lemma}
\renewcommand\qedsymbol{\hfill$\blacksquare$}
\newtheorem*{remark}{Remark}

\newenvironment{myproof}[1][\proofname\renewcommand*{\qedsymbol}{\(\blacksquare\)}]{
  \it\hspace{-1.55em}Proof.\hspace{0.55em}\normalfont
}\qedsymbol{\endproof}








