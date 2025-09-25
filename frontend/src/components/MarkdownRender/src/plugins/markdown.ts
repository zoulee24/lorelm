import MarkdownIt from 'markdown-it'
import markdownItKatex from '@vscode/markdown-it-katex'
import splitAtDelimiters from 'katex/contrib/auto-render/splitAtDelimiters.js'
import 'katex/dist/katex.min.css'
import 'katex/dist/contrib/mhchem.mjs'

const md = new MarkdownIt({
  html: true,
  linkify: false,
  typographer: true
}).use(markdownItKatex)

const transformThinkMarkdown = (markdownText: string) => { 
  // 匹配以*$开通并且以$*结尾(中间可以包括换行)
  return markdownText.replace(/@\$(.*?)\$\@/g, (match, p1) => {
    return `<p class="think">${p1}</p>`
  })
}

const transformEmphasizeMarkdown = (markdownText: string) => { 
  // 匹配以*$开通并且以$*结尾(中间不可以包括换行)
  return markdownText.replace(/\*\$(.*?)\$\*/g, (match, p1) => {
    return `<span class="emphasize">${p1}</span>`
  })
}

const transformActionMarkdown = (markdownText: string) => { 
  // 匹配以*$开通并且以$*结尾(中间不可以包括换行)
  return markdownText.replace(/\^\$(.*?)\$\^/g, (match, p1) => {
    return `<span class="action">${p1}</span>`
  })
}

const transformMathMarkdown = (markdownText: string) => {
  const data = splitAtDelimiters(markdownText, [
    {
      left: '\\[',
      right: '\\]',
      display: true
    },
    {
      left: '\\(',
      right: '\\)',
      display: false
    }
  ])

  return data.reduce((result: string, segment: any) => {
    if (segment.type === 'text') {
      return result + segment.data
    }
    const math = segment.display ? `$$${ segment.data }$$` : `$${ segment.data }$`
    return result + math
  }, '')
}

export const renderMarkdownText = (content: string) => {
  content = transformThinkMarkdown(content)
  content = transformEmphasizeMarkdown(content)
  content = transformActionMarkdown(content)
  // const thinkTransformed = transformThinkMarkdown(content)
  // content = transformMathMarkdown(content)
  return md.render(content)
}