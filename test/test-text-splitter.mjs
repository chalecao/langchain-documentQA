/**
 * node --experimental-modules tt.mjs
 */
// import { Document } from "langchain/document";

// import { CharacterTextSplitter } from "langchain/text_splitter";



// const text = "foo bar baz 123";

// const splitter = new CharacterTextSplitter({
//   separator: "",  // 分隔符

//   chunkSize: 7,   // 每个块中最大字符数。默认值为1000个标记（tokens)

//   chunkOverlap: 3,  // 相邻块之间重叠的字符数。默认值为200个标记（tokens)

// });

// const output = await splitter.createDocuments([text]);
// console.log(output);


import { Document } from "langchain/document";

import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";

const text = `Hi.I'm Harrison.How? Are? You?Okay then f f f f. 

This is a weird text to write, but gotta test the splittingggg some how. 

Bye!-H.`;

const splitter = new RecursiveCharacterTextSplitter({

  chunkSize: 100,

  chunkOverlap: 20,

});

const docOutput = await splitter.splitDocuments([

  new Document({ pageContent: text }),

]);

console.log(docOutput)