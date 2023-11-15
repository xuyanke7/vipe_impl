## About TestCase
---
### Links
* [Test Case Design: a Guide for QA Engineers With Examples](https://www.testim.io/blog/test-case-design-guide-for-qa-engineers/)
### Notion
* 包括input、execution conditions, testing procedure, and expected results
* 对于每一个requirement,contain one positive test and one negative test.(formal test cases)
### Written format
*              
### Design technique
* Boundary Value Analysis (BVA)
includes maximun,minumin,inside or outside boundaries,typical values and error values.
(so did the ViperGPT get the wrong answer more at the boundaries of the input? And what is the boundary of the input image/query at GQA situation? )

* Equivalence Class Partitioning (EP)

* Decision Table Testing
The output depends on a combination of inputs.

* State Transition Diagrams

* Use Case Testing

### other
* 将query和image caption和scene graph caption输入
* 将GQA dataset构建中的five evaluation metrics应用到通过feedback修改生成的代码中
    * Consistency:
    * validity and plausibility:
    * distribution
    * grounding
    