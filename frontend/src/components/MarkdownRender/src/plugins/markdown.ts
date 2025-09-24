import MarkdownIt from 'markdown-it'
import markdownItKatex from '@vscode/markdown-it-katex'
import splitAtDelimiters from 'katex/contrib/auto-render/splitAtDelimiters.js'
import 'katex/dist/katex.min.css'
import 'katex/dist/contrib/mhchem.mjs'

const md = new MarkdownIt({
  html: false,
  linkify: false,
  typographer: true
}).use(markdownItKatex)


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
  // const thinkTransformed = transformThinkMarkdown(content)
  content = transformMathMarkdown(content)
  return md.render(content)
}