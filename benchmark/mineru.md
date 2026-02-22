arXiv:2501.17887v1 [cs.CL] 27 Jan 2025
# Docling: An Efficient Open-Source Toolkit for AI-driven Document Conversion
# Nikolaos Livathinos *, Christoph Auer *, Maksym Lysak, Ahmed Nassar, Michele Dolfi,Panagiotis Vagenas, Cesar Berrospi, Matteo Omenetti, Kasper Dinkla, Yusik Kim,Shubham Gupta, Rafael Teixeira de Lima, Valery Weber, Lucas Morin, Ingmar Meijer,Viktor Kuropiatnyk, Peter W. J. Staar
IBM Research, Ruschlikon, Switzerland ¨
Please send correspondence to: deepsearch-core@zurich.ibm.com
# Abstract
We introduce Docling, an easy-to-use, self-contained, MIT-licensed, open-source toolkit for document conversion, thatcan parse several types of popular document formats intoa unified, richly structured representation. It is powered bystate-of-the-art specialized AI models for layout analysis(DocLayNet) and table structure recognition (TableFormer),and runs efficiently on commodity hardware in a small re-source budget. Docling is released as a Python package andcan be used as a Python API or as a CLI tool. Docling’s mod-ular architecture and efficient document representation makeit easy to implement extensions, new features, models, andcustomizations. Docling has been already integrated in otherpopular open-source frameworks (e.g., LangChain, LlamaIn-dex, spaCy), making it a natural fit for the processing of doc-uments and the development of high-end applications. Theopen-source community has fully engaged in using, promot-ing, and developing for Docling, which gathered 10k stars onGitHub in less than a month and was reported as the No. 1trending repository in GitHub worldwide in November 2024.
Repository — https://github.com/DS4SD/docling
# 1 Introduction
Converting documents back into a unified machine-processable format has been a major challenge for decadesdue to their huge variability in formats, weak standardizationand printing-optimized characteristic, which often discardsstructural features and metadata. With the advent of LLMsand popular application patterns such as retrieval-augmentedgeneration (RAG), leveraging the rich content embedded inPDFs, Office documents, and scanned document images hasbecome ever more relevant. In the past decade, several pow-erful document understanding solutions have emerged onthe market, most of which are commercial software, SaaSofferings on hyperscalers (Auer et al. 2022) and most re-cently, multimodal vision-language models. Typically, theyincur a cost (e.g., for licensing or LLM inference) and cannotbe run easily on local hardware. Meanwhile, only a hand-ful of different open-source tools cover PDF, MS Word, MSPowerPoint, Images, or HTML conversion, leaving a signif-icant feature and quality gap to proprietary solutions.
With Docling, we recently open-sourced a very capa-ble and efficient document conversion tool which builds onthe powerful, specialized AI models and datasets for layoutanalysis and table structure recognition that we developedand presented in the recent past (Livathinos et al. 2021; Pfitz-mann et al. 2022; Lysak et al. 2023). Docling is designedas a simple, self-contained Python library with permissiveMIT license, running entirely locally on commodity hard-ware. Its code architecture allows for easy extensibility andaddition of new features and models. Since its launch in July2024, Docling has attracted considerable attention in the AIdeveloper community and ranks top on GitHub’s monthlytrending repositories with more than 10,000 stars at the timeof writing. On October 16, 2024, Docling reached a majormilestone with version 2, introducing several new featuresand concepts, which we outline in this updated technical re-port, along with details on its architecture, conversion speedbenchmarks, and comparisons to other open-source assets.
The following list summarizes the features currentlyavailable on Docling:
• Parses common document formats (PDF, Images, MSOffice formats, HTML) and exports to Markdown,JSON, and HTML.
• Applies advanced AI for document understanding, in-cluding detailed page layout, OCR, reading order, figureextraction, and table structure recognition.
• Establishes a unified DoclingDocument data modelfor rich document representation and operations.
• Provides fully local execution capabilities making it suit-able for sensitive data and air-gapped environments.
• Has an ecosystem of plug-and-play integrations withprominent generative AI development frameworks, in-cluding LangChain and LlamaIndex.
• Can leverage hardware accelerators such as GPUs.
# 2 State of the Art
Document conversion is a well-established field with numer-ous solutions already available on the market. These solu-tions can be categorized along several key dimensions, in-cluding open vs. closed source, permissive vs. restrictive li-censing, Web APIs vs. local code deployment, susceptibility
*These authors contributed equally.Copyright $^ ©$ 2025, Association for the Advancement of ArtificialIntelligence (www.aaai.org). All rights reserved.
![image](/6f3591a97a185155e57f1c985f78a9f4a2b4b0383905ff41284c4609c1e102d0.jpg)


Figure 1: Sketch of Docling’s pipelines and usage model. Both PDF pipeline and simple pipeline build up aDoclingDocument representation, which can be further enriched. Downstream applications can utilize Docling’s API toinspect, export, or chunk the document for various purposes.

to hallucinations, conversion quality, time-to-solution, andcompute resource requirements.
The most popular conversion tools today leverage vision-language models (VLMs), which process page images totext and markup directly. Among proprietary solutions,prominent examples include GPT-4o (OpenAI), Claude(Anthropic), and Gemini (Google). In the open-source do-main, LLaVA-based models, such as LLaVA-next, are note-worthy. However, all generative AI-based models face twosignificant challenges. First, they are prone to hallucina-tions, i.e., their output may contain false information whichis not present in the source document — a critical issuewhen faithful transcription of document content is required.Second, these models demand substantial computational re-sources, making the conversion process expensive. Conse-quently, VLM-based tools are typically offered as SaaS,with compute-intensive operations performed remotely inthe cloud.
A second category of solutions prioritizes on-premisesdeployment, either as Web APIs or as libraries. Examplesinclude Adobe Acrobat, Grobid, Marker, MinerU, Unstruc-tured, and others. These solutions often rely on multiple spe-cialized models, such as OCR, layout analysis, and tablerecognition models. Docling falls into this category, leverag-ing modular, task-specific models which recover documentstructures and features only. All text content is taken fromthe programmatic PDF or transcribed through OCR meth-ods. This design ensures faithful conversion, without the riskof generating false content. However, it necessitates main-taining a diverse set of models for different document com-ponents, such as formulas or figures.
Within this category, Docling distinguishes itself throughits permissive MIT license, allowing organizations to inte-grate Docling into their solutions without incurring licens-ing fees or adopting restrictive licenses (e.g., GPL). Addi-
tionally, Docling offers highly accurate, resource-efficient,and fast models, making it well-suited for integration withmany standard frameworks.
In summary, Docling stands out as a cost-effective, accu-rate and transparent open-source library with a permissive li-cense, offering a reliable and flexible solution for documentconversion.
# 3 Design and Architecture
Docling is designed in a modular fashion with extensibil-ity in mind, and it builds on three main concepts: pipelines,parser backends, and the DoclingDocument data modelas its centerpiece (see Figure 1). Pipelines and parser back-ends share the responsibility of constructing and enrichinga DoclingDocument representation from any supportedinput format. The DoclingDocument data model with itsAPIs enable inspection, export, and downstream processingfor various applications, such as RAG.
# 3.1 Docling Document
Docling v2 introduces a unified document representation,DoclingDocument, as a Pydantic data model that can ex-press various common document features, such as:
• Text, Tables, Pictures, Captions, Lists, and more.
• Document hierarchy with sections and groups.
• Disambiguation between main body and headers, footers(furniture).
• Layout information (i.e., bounding boxes) for all items,if available.
• Provenance information (i.e., page numbers, documentorigin).
With this data model, Docling enables representing doc-ument content in a unified manner, i.e., regardless of thesource document format.
Besides specifying the data model, theDoclingDocument class defines APIs encompass-ing document construction, inspection, and export. Usingthe respective methods, users can incrementally build aDoclingDocument, traverse its contents in readingorder, or export to commonly used formats. Doclingsupports lossless serialization to (and deserialization from)JSON, and lossy export formats such as Markdown andHTML, which, unlike JSON, cannot retain all availablemeta information.
A DoclingDocument can additionally be passed to achunker class, an abstraction that returns a stream of chunks,each of which captures some part of the document as a stringaccompanied by respective metadata. To enable both flexi-bility for downstream applications and out-of-the-box util-ity, Docling defines a chunker class hierarchy, providing abase type as well as specific subclasses. By using the basechunker type, downstream applications can leverage popularframeworks like LangChain or LlamaIndex, which providea high degree of flexibility in the chunking approach. Userscan therefore plug in any built-in, self-defined, or third-partychunker implementation.
# 3.2 Parser Backends
Document formats can be broadly categorized into twotypes:
1. Low-level formats, like PDF files or scanned images.These formats primarily encode the visual representationof the document, containing instructions for renderingtext cells and lines or defining image pixels. Most seman-tics of the represented content are typically lost and needto be recovered through specialized AI methods, such asOCR, layout analysis, or table structure recognition.
2. Markup-based formats, including MS Office, HTML,Markdown, and others. These formats preserve the se-mantics of the content (e.g., sections, lists, tables, andfigures) and are comparatively inexpensive to parse.
Docling implements several parser backends to read andinterpret different formats and it routes their output to a fit-ting processing pipeline. For PDFs Docling provides back-ends which: a) retrieve all text content and their geomet-ric properties, b) render the visual representation of eachpage as it would appear in a PDF viewer. For markup-basedformats, the respective backends carry the responsibility ofcreating a DoclingDocument representation directly. Forsome formats, such as PowerPoint slides, element locationsand page provenance are available, whereas in other formats(for example, MS Word or HTML), this information is un-known unless rendered in a Word viewer or a browser. TheDoclingDocument data model handles both cases.
PDF Backends While several open-source PDF parsingPython libraries are available, in practice we ran into vari-ous limitations, among which are restrictive licensing (e.g.,
pymupdf (pym 2024)), poor speed, or unrecoverable qual-ity issues, such as merged text cells across far-apart text to-kens or table columns (pypdfium, PyPDF) (PyPDFium Team2024; pypdf Maintainers 2024).
We therefore developed a custom-built PDF parser, whichis based on the low-level library qpdf (Berkenbilt 2024). OurPDF parser is made available in a separate package nameddocling-parse and acts as the default PDF backend in Do-cling. As an alternative, we provide a PDF backend relyingon pypdfium (PyPDFium Team 2024).
Other Backends Markup-based formats like HTML,Markdown, or Microsoft Office (Word, PowerPoint, Ex-cel) as well as plain formats like AsciiDoc can be trans-formed directly to a DoclingDocument representationwith the help of several third-party format parsing libraries.For HTML documents we utilize BeautifulSoup (Richard-son 2004–2024), for Markdown we use the Marko li-brary (Ming 2019–2024), and for Office XML-based for-mats (Word, PowerPoint, Excel) we implement custom ex-tensions on top of the python-docx (Canny and contributors2013–2024a), python-pptx (Canny and contributors 2013–2024b), and openpyxl (Eric Gazoni 2010–2024) libraries, re-spectively. During parsing, we identify and extract commondocument elements (e.g., title, headings, paragraphs, tables,lists, figures, and code) and reflect the correct hierarchy levelif possible.
# 3.3 Pipelines
Pipelines in Docling serve as an orchestration layer whichiterates through documents, gathers the extracted data froma parser backend, and applies a chain of models to: a) buildup the DoclingDocument representation and b) enrichthis representation further (e.g., classify images).
Docling provides two standard pipelines. The Standard-PdfPipeline leverages several state-of-the-art AI models toreconstruct a high-quality DoclingDocument representationfrom PDF or image input, as described in section 4. TheSimplePipeline handles all markup-based formats (Office,HTML, AsciiDoc) and may apply further enrichment mod-els as well.
Pipelines can be fully customized by sub-classing froman abstract base class or cloning the default model pipeline.This effectively allows to fully customize the chain of mod-els, add or replace models, and introduce additional pipelineconfiguration parameters. To create and use a custom modelpipeline, you can provide a custom pipeline class as an ar-gument to the main document conversion API.
# 4 PDF Conversion Pipeline
The capability to recover detailed structure and content fromPDF and image files is one of Docling’s defining features. Inthis section, we outline the underlying methods and modelsthat drive the system.
Each document is first parsed by a PDF backend, whichretrieves the programmatic text tokens, consisting of stringcontent and its coordinates on the page, and also renders abitmap image of each page to support downstream opera-tions. Any image format input is wrapped in a PDF container
on the fly, and proceeds through the pipeline as a scannedPDF document. Then, the standard PDF pipeline applies asequence of AI models independently on every page of thedocument to extract features and content, such as layout andtable structures. Finally, the results from all pages are ag-gregated and passed through a post-processing stage, whicheventually assembles the DoclingDocument representa-tion.
# 4.1 AI Models
As part of Docling, we release two highly capable AI mod-els to the open-source community, which have been devel-oped and published recently by our team. The first modelis a layout analysis model, an accurate object detector forpage elements (Pfitzmann et al. 2022). The second modelis TableFormer (Nassar et al. 2022; Lysak et al. 2023), astate-of-the-art table structure recognition model. We pro-vide the pre-trained weights (hosted on Hugging Face) anda separate Python package for the inference code (docling-ibm-models).
Layout Analysis Model Our layout analysis model isan object detector which predicts the bounding-boxes andclasses of various elements on the image of a given page. Itsarchitecture is derived from RT-DETR (Zhao et al. 2023) andre-trained on DocLayNet (Pfitzmann et al. 2022), our pop-ular human-annotated dataset for document-layout analysis,among other proprietary datasets. For inference, our imple-mentation relies on the Hugging Face transformers (Wolfet al. 2020) library and the Safetensors file format. All pre-dicted bounding-box proposals for document elements arepost-processed to remove overlapping proposals based onconfidence and size, and then intersected with the text to-kens in the PDF to group them into meaningful and completeunits such as paragraphs, section titles, list items, captions,figures, or tables.
Table Structure Recognition The TableFormermodel (Nassar et al. 2022), first published in 2022 andsince refined with a custom structure token language (Lysaket al. 2023), is a vision-transformer model for table structurerecovery. It can predict the logical row and column structureof a given table based on an input image, and determinewhich table cells belong to column headers, row headersor the table body. Compared to earlier approaches, Table-Former handles many characteristics of tables like partialor no borderlines, empty cells, rows or columns, cell spansand hierarchy on both column-heading and row-headinglevel, tables with inconsistent indentation or alignmentand other complexities. For inference, our implementationrelies on PyTorch (Ansel et al. 2024). The PDF pipelinefeeds all table objects detected in the layout analysis tothe TableFormer model, by providing an image-crop ofthe table and the included text cells. TableFormer structurepredictions are matched back to the PDF cells during apost-processing step, to avoid expensive re-transcription ofthe table image-crop, which also makes the TableFormermodel language agnostic.
OCR Docling utilizes OCR to convert scanned PDFs andextract content from bitmaps images embedded in a page.Currently, we provide integration with EasyOCR (eas 2024),a popular third-party OCR library with support for manylanguages, and Tesseract as a widely available alternative.While EasyOCR delivers reasonable transcription quality,we observe that it runs fairly slow on CPU (see section 5),making it the biggest compute expense in the pipeline.
Assembly In the final pipeline stage, Docling assemblesall prediction results produced on each page into the Do-clingDocument representation, as defined in the auxiliaryPython package docling-core. The generated document ob-ject is passed through a post-processing model which lever-ages several algorithms to augment features, such as correct-ing the reading order or matching figures with captions.
# 5 Performance
In this section, we characterize the conversion speed of PDFdocuments with Docling in a given resource budget for dif-ferent scenarios and establish reference numbers.
Further, we compare the conversion speed to three pop-ular contenders in the open-source space, namely unstruc-tured.io (Unstructured.io Team 2024), Marker (Paruchuri2024), and MinerU (Wang et al. 2024). All aforementionedsolutions can universally convert PDF documents to Mark-down or similar representations and offer a library-style in-terface to run the document processing entirely locally. Weexclude SaaS offerings and remote services for documentconversion from this comparison, since the latter do not pro-vide any possibility to control the system resources they runon, rendering any speed comparison invalid.
# 5.1 Benchmark Dataset
To enable a meaningful benchmark, we composed a testset of 89 PDF files covering a large variety of styles, fea-tures, content, and length (see Figure 2). This dataset isbased to a large extend on our DocLayNet (Pfitzmann et al.2022) dataset and augmented with additional samples fromCCpdf (Turski et al. 2023) to increase the variety. Overall,it includes 4008 pages, 56246 text items, 1842 tables and4676 pictures. As such, it is large enough to provide varietywithout requiring excessively long benchmarking times.
# 5.2 System Configurations
We schedule our benchmark experiments each on two dif-ferent systems to create reference numbers:
• AWS EC2 VM (g6.xlarge), 8 virtual cores (AMD EPYC7R13, x86), 32 GB RAM, Nvidia L4 GPU (24 GBVRAM), on Ubuntu 22.04 with Nvidia CUDA 12.4drivers
• MacBook Pro M3 Max (ARM), 64GB RAM, on macOS14.7
All experiments on the AWS EC2 VM are carried outonce with GPU acceleration enabled and once purely onthe $\mathbf { \boldsymbol { x } } 8 6$ CPU, resulting in three total system configurationswhich we refer to as M3 Max SoC, L4 GPU, and $\mathbf { \boldsymbol { x } } 8 6$ CPU.

Table 1: Versions and configuration options considered for each tested asset. * denotes the default setting.

<table><tr><td>Asset</td><td>Version</td><td>OCR</td><td>Layout</td><td>Tables</td></tr><tr><td>Docling</td><td>2.5.2</td><td>EasyOCR*</td><td>default</td><td>TableFormer (fast)*</td></tr><tr><td>Marker</td><td>0.3.10</td><td>Surya*</td><td>default</td><td>default</td></tr><tr><td>MinerU</td><td>0.9.3</td><td>auto*</td><td>doclayout_yolo</td><td>rapid_table*</td></tr><tr><td>Unstructured</td><td>0.16.5</td><td></td><td colspan="2">hi_res with table structure</td></tr></table>
![image](/a2d74eeff41689782ed4f11a10c0f6bafc18915d32ee1d3f21c53adda7e84d3f.jpg)

![image](/830ae49911e8e3e610f87d2e07e8069e8dd03809480fa649915b734587f973c7.jpg)


Figure 2: Dataset categories and sample counts for docu-ments and pages.

# 5.3 Benchmarking Methodology
We implemented several measures to enable a fair and re-producible benchmark across all tested assets. Specifically,the experimental setup accounts for the following factors:
• All assets are installed in the latest available versions,in a clean Python environment, and configured to use thestate-of-the-art processing options and models, where ap-plicable. We selectively disabled non-essential function-alities to achieve a compatible feature-set across all com-pared libraries.
• When running experiments on CPU, we inform all assetsof the desired CPU thread budget of 8 threads, via theOMP NUM THREADS environment variable and any ac-cepted configuration options. The L4 GPU on our AWSEC2 VM is hidden.
• When running experiments on the L4 GPU, we enableCUDA acceleration in all accepted configuration options,ensure the GPU is visible and all required runtimes for AIinference are installed with CUDA support.
Table 1 provides an overview of the versions and config-uration options we considered for each asset.
# 5.4 Results
![image](/95e2ffae7ccd0ca3e11c7869774604646e0e0fc258e5f109c177e1463d88aa85.jpg)


Figure 3: Distribution of conversion times for all documents,ordered by number of pages in a document, on all systemconfigurations. Every dot represents one document. Log/logscale is used to even the spacing, since both number of pagesand conversion times have long-tail distributions.

Runtime Characteristics To analyze Docling’s runtimecharacteristics, we begin by exploring the relationship be-tween document length (in pages) and conversion time. Asshown in Figure 3, this relationship is not strictly linear, asdocuments differ in their frequency of tables and bitmap el-ements (i.e., scanned content). This requires OCR or tablestructure recognition models to engage dynamically whenlayout analysis has detected such elements.
By breaking down the runtimes to a page level, we receivea more intuitive measure for the conversion speed (see alsoFigure 4). Processing a page in our benchmark dataset re-quires between 0.6 sec $5 ^ { \mathrm { { \bar { t h } } } }$ percentile) and 16.3 sec $9 5 ^ { \mathrm { t h } }$ per-centile), with a median of 0.79 sec on the x86 CPU. On theM3 Max SoC, it achieves $0 . 2 6 / 0 . 3 2 / 6 . 4 8$ seconds per page(.05/median/.95), and on the Nvidia L4 GPU it achieves57/114/2081 milliseconds per page (.05/median/.95). The
large range between 5 and 95 percentiles results from thehighly different complexity of content across pages (i.e., al-most empty pages vs. full-page tables).
Disabling OCR saves $60 \%$ of runtime on the $\mathbf { \boldsymbol { x } } 8 6$ CPU andthe M3 Max SoC, and $50 \%$ on the L4 GPU. Turning off tablestructure recognition saves $16 \%$ of runtime on the $\mathbf { \boldsymbol { x } } 8 6$ CPUand the M3 Max SoC, and $24 \%$ on the L4 GPU. Disablingboth OCR and table structure recognition saves around $7 5 \%$of runtime on all system configurations.
Profiling Docling’s AI Pipeline We analyzed the contri-butions of Docling’s PDF backend and all AI models in thePDF pipeline to the total conversion time. The results areshown in Figure 4. On average, processing a page took 481ms on the L4 GPU, 3.1 s on the $\mathbf { \boldsymbol { x } } 8 6$ CPU and 1.26 s on theM3 Max SoC.
It is evident that applying OCR is the most expensiveoperation. In our benchmark dataset, OCR engages in 578pages. On average, transcribing a page with EasyOCR took1.6 s on the L4 GPU, 13 s on the $\mathbf { \boldsymbol { x } } 8 6$ CPU and 5 s on the M3Max SoC. The layout model spent 44 ms on the L4 GPU,633 ms on the $\mathbf { \boldsymbol { x } } 8 6$ CPU and 271 ms on the M3 Max SoCon average for each page, making it the cheapest of the AImodels, while TableFormer (fast flavour) spent 400 ms onthe L4 GPU, 1.74 s on the $\mathbf { \boldsymbol { x } } 8 6$ CPU and 704 ms on theM3 Max SoC on average per table. Regarding the total timespent converting our benchmark dataset, TableFormer hadless impact than other AI models, since tables appeared ononly $28 \%$ of all pages (see Figure 4).
On the L4 GPU, we observe a speedup of 8x (OCR), 14x(Layout model) and $4 . 3 \mathrm { x }$ (Table structure) compared to the$\mathbf { \boldsymbol { x } } 8 6$ CPU and a speedup of 3x (OCR), 6x (Layout model)and $1 . 7 \mathrm { x }$ (Table structure) compared to the M3 Max CPU ofour MacBook Pro. This shows that there is no equal benefitfor all AI models from the GPU acceleration and there mightbe potential for optimization.
The time spent in parsing a PDF page through ourdocling-parse backend is substantially lower in comparisonto the AI models. On average, parsing a PDF page took 81ms on the $\mathbf { \boldsymbol { x } } 8 6$ CPU and 44 ms on the M3 Max SoC (there isno GPU support).
Comparison to Other Tools We compare the averagetimes to convert a page between Docling, Marker, MinerU,and Unstructured on the system configurations outlined insection 5.2. Results are shown in Figure 5.
Without GPU support, Docling leads with 3.1 sec/page(x86 CPU) and 1.27 sec/page (M3 Max SoC), followedclosely by MinerU (3.3 sec/page on $\mathbf { \boldsymbol { x } } 8 6$ CPU) and Unstruc-tured (4.2 sec/page on $\mathbf { \boldsymbol { x } } 8 6$ CPU, 2.7 sec/page on M3 MaxSoC), while Marker needs over 16 sec/page (x86 CPU) and4.2 sec/page (M3 Mac SoC). MinerU, despite several effortsto configure its environment, did not finish any run on ourMacBook Pro M3 Max. With CUDA acceleration on theNvidia L4 GPU, the picture changes and MinerU takes thelead over the contenders with 0.21 sec/page, compared to0.49 sec/page with Docling and 0.86 sec/page with Marker.Unstructured does not profit from GPU acceleration.
# 6 Applications
Docling’s document extraction capabilities make it naturallysuitable for workflows like generative AI applications (e.g.,RAG), data preparation for foundation model training, andfine-tuning, as well as information extraction.
As far as RAG is concerned, users can leverage existingDocling extensions for popular frameworks like LlamaIn-dex and then harness framework capabilities for RAG com-ponents like embedding models, vector stores, etc. TheseDocling extensions typically provide two modes of opera-tion: one using a lossy export, e.g., to Markdown, and oneusing lossless serialization via JSON. The former providesa simple starting point, upon which any text-based chunk-ing method may be applied (e.g., also drawing from theframework library), while the latter, which uses a swappableDocling chunker type, can be the more powerful one, as itcan provide document-native RAG grounding via rich meta-data such as the page number and the bounding box of thesupporting context. For usage outside of these frameworks,users can still employ Docling chunkers to accelerate andsimplify the development of their custom pipelines. Besidesstrict RAG pipelines for Q&A, Docling can naturally be uti-lized in the context of broader agentic workflows for whichit can provide document-based knowledge for agents to de-cide and act on.
Moreover, Docling-enabled pipelines can generateground truth data out of documents. Such domain-specificknowledge can make significant impact when infused tofoundation model training and fine-tuning.
Last but not least, Docling can be used as a backbonefor information extraction tasks. Users who seek to cre-ate structured representations out of unstructured documentscan leverage Docling, which maps various document for-mats to the unified DoclingDocument format, as wellas its strong table understanding capabilities that can helpbetter analyze semi-structured document parts.
# 7 Ecosystem
Docling is quickly evolving into a mainstream package fordocument conversion. The support for PDF, MS Office for-mats, Images, HTML, and more makes it a universal choicefor downstream applications. Users appreciate the intuitive-ness of the library, the high-quality, richly structured conver-sion output, as well as the permissive MIT license, and thepossibility of running entirely locally on commodity hard-ware.
Among the integrations created by the Docling teamand the growing community, a few are worth mention-ing as depicted in Figure 6. For popular generative AIapplication patterns, we provide native integration withinLangChain (Chase 2022) and LlamaIndex (Liu 2022) forreading documents and chunking. Processing and transform-ing documents at scale for building large-scale multi-modaltraining datasets are enabled by the integration in the openIBM data-prep-kit (Wood et al. 2024). Agentic workloadscan leverage the integration with the Bee framework (IBMResearch 2024). For the fine-tuning of language models, Do-cling is integrated in InstructLab (Sudalairaj et al. 2024),
![image](/72b3fa8a15ad64189d4da8a7f9b1691c310edab480bfb7b037de0af545340d30.jpg)

![image](/6c59918e556a554e30240079f26016dd7591e1bd1e9334d596902c958fd8c22e.jpg)


Figure 4: Contributions of PDF backend and AI models to the conversion time of a page (in seconds per page). Lower is better.Left: Ranges of time contributions for each model to pages it was applied on (i.e., OCR was applied only on pages with bitmaps,table structure was applied only on pages with tables). Right: Average time contribution to a page in the benchmark dataset(factoring in zero-time contribution for OCR and table structure models on pages without bitmaps or tables) .

![image](/2552bf2a9f837ba353e3d80ad72897f27975b97f4739cdda03af510b79c9766b.jpg)


Figure 5: Conversion time in seconds per page on our datasetin three scenarios, across all assets and system configura-tions. Lower bars are better. The configuration includes OCRand table structure recognition (fast table option on Do-cling and MinerU, hi res in unstructured, as shown in ta-ble 1).

where it supports the enhancement of the knowledge tax-onomy.
Docling is also available and officially maintained asa system package in the Red $\mathrm { H a t } ^ { \circledast }$ Enterprise Linux® AI(RHEL AI) distribution, which seamlessly allows to de-velop, test, and run the Granite family of large languagemodels for enterprise applications.
![image](/138df27aa3fa5b82eddf82ad24d15f360ecdd54e615d0a6845453012627970d4.jpg)


Figure 6: Ecosystem of Docling integrations contributed bythe Docling team or the broader community. Docling is al-ready used for RAG, model fine-tuning, large-scale datasetscreation, information extraction and agentic workflows.

# 8 Future Work and Contributions
Docling’s modular architecture allows an easy extension ofthe model library and pipelines. In the future, we plan toextend Docling with several additional models, such as afigure-classifier model, an equation-recognition model anda code-recognition model. This will help improve the qual-ity of conversion for specific types of content, as well asaugment extracted document metadata with additional in-formation. Furthermore, we will focus on building an open-source quality evaluation framework for the tasks performedby Docling, such as layout analysis, table structure recog-nition, reading order detection, text transcription, etc. Thiswill allow transparent quality comparisons based on publiclyavailable benchmarks such as DP-Bench (Zhong 2020), Om-nidDocBench(Ouyang et al. 2024) and others. Results willbe published in a future update of this technical report.
The codebase of Docling is open for use under the MIT
license agreement and its roadmap is outlined in the discus-sions section 1 of our GitHub repository. We encourage ev-eryone to propose improvements and make contributions.
# References


2024. EasyOCR: Ready-to-use OCR with $8 0 +$ supportedlanguages. https://github.com/JaidedAI/EasyOCR.




2024. PyMuPDF. https://github.com/pymupdf/PyMuPDF.




Ansel, J.; Yang, E.; He, H.; et al. 2024. PyTorch 2:Faster Machine Learning Through Dynamic Python Byte-code Transformation and Graph Compilation. In Proceed-ings of the 29th ACM International Conference on Architec-tural Support for Programming Languages and OperatingSystems, Volume 2 (ASPLOS ’24). ACM.




Auer, C.; Dolfi, M.; Carvalho, A.; Ramis, C. B.; and Staar,P. W. 2022. Delivering Document Conversion as a CloudService with High Throughput and Responsiveness. In 2022IEEE 15th International Conference on Cloud Computing(CLOUD), 363–373. IEEE.




Berkenbilt, J. 2024. QPDF: A Content-Preserving PDF Doc-ument Transformer. https://github.com/qpdf/qpdf.




Canny, S.; and contributors. 2013–2024a. python-docx: Cre-ate and update Microsoft Word .docx files with Python.https://python-docx.readthedocs.io/.




Canny, S.; and contributors. 2013–2024b. python-pptx:Python library for creating and updating PowerPoint (.pptx)files. https://python-pptx.readthedocs.io/.




Chase, H. 2022. LangChain. https://github.com/langchain-ai/langchain.




Eric Gazoni, C. C. 2010–2024. openpyxl: A Pythonlibrary to read/write Excel 2010 xlsx/xlsm files.https://openpyxl.readthedocs.io/.




IBM Research. 2024. Bee Agent Framework.https://github.com/i-am-bee/bee-agent-framework.




Liu, J. 2022. LlamaIndex. https://github.com/jerryjliu/llama index.




Livathinos, N.; Berrospi, C.; Lysak, M.; Kuropiatnyk, V.;Nassar, A.; Carvalho, A.; Dolfi, M.; Auer, C.; Dinkla, K.;and Staar, P. 2021. Robust PDF Document Conversion us-ing Recurrent Neural Networks. Proceedings of the AAAIConference on Artificial Intelligence, 35(17): 15137–15145.




Lysak, M.; Nassar, A.; Livathinos, N.; Auer, C.; and Staar,P. 2023. Optimized Table Tokenization for Table Struc-ture Recognition. In Document Analysis and Recognition- ICDAR 2023: 17th International Conference, San Jose,´CA, USA, August 21–26, 2023, Proceedings, Part II, 37–50. Berlin, Heidelberg: Springer-Verlag. ISBN 978-3-031-41678-1.




Ming, F. 2019–2024. Marko: A markdown parser with highextensibility. https://github.com/frostming/marko.




Nassar, A.; Livathinos, N.; Lysak, M.; and Staar, P. 2022.Tableformer: Table structure understanding with transform-ers. In Proceedings of the IEEE/CVF Conference on Com-puter Vision and Pattern Recognition, 4614–4623.




Ouyang, L.; Qu, Y.; Zhou, H.; Zhu, J.; Zhang, R.; Lin, Q.;Wang, B.; Zhao, Z.; Jiang, M.; Zhao, X.; Shi, J.; Wu, F.;Chu, P.; Liu, M.; Li, Z.; Xu, C.; Zhang, B.; Shi, B.; Tu, Z.;and He, C. 2024. OmniDocBench: Benchmarking DiversePDF Document Parsing with Comprehensive Annotations.arXiv:2412.07626.




Paruchuri, V. 2024. Marker: Convert PDFto Markdown Quickly with High Accuracy.https://github.com/VikParuchuri/marker.




Pfitzmann, B.; Auer, C.; Dolfi, M.; Nassar, A. S.; and Staar,P. 2022. DocLayNet: a large human-annotated dataset fordocument-layout segmentation. 3743–3751.




pypdf Maintainers. 2024. pypdf: A Pure-Python PDF Li-brary. https://github.com/py-pdf/pypdf.




PyPDFium Team. 2024. PyPDFium2: Python bindings forPDFium. https://github.com/pypdfium2-team/pypdfium2.




Richardson, L. 2004–2024. Beautiful Soup: APython library for parsing HTML and XML.https://www.crummy.com/software/BeautifulSoup/.




Sudalairaj, S.; Bhandwaldar, A.; Pareja, A.; Xu, K.; Cox,D. D.; and Srivastava, A. 2024. LAB: Large-Scale Align-ment for ChatBots. arXiv:2403.01081.




Turski, M.; Stanisławek, T.; Kaczmarek, K.; Dyda, P.; andGralinski, F. 2023. CCpdf: Building a High Quality Corpus ´for Visually Rich Documents from Web Crawl Data. In Fink,G. A.; Jain, R.; Kise, K.; and Zanibbi, R., eds., DocumentAnalysis and Recognition - ICDAR 2023, 348–365. Cham:Springer Nature Switzerland. ISBN 978-3-031-41682-8.




Unstructured.io Team. 2024. Unstructured.io: Open-Source Pre-Processing Tools for Unstructured Data.https://unstructured.io. Accessed: 2024-11-19.




Wang, B.; Xu, C.; Zhao, X.; Ouyang, L.; Wu, F.; Zhao, Z.;Xu, R.; Liu, K.; Qu, Y.; Shang, F.; Zhang, B.; Wei, L.; Sui,Z.; Li, W.; Shi, B.; Qiao, Y.; Lin, D.; and He, C. 2024.MinerU: An Open-Source Solution for Precise DocumentContent Extraction. arXiv:2409.18839.




Wolf, T.; Debut, L.; Sanh, V.; Chaumond, J.; Delangue, C.;Moi, A.; Cistac, P.; Rault, T.; Louf, R.; Funtowicz, M.; Davi-son, J.; Shleifer, S.; von Platen, P.; Ma, C.; Jernite, Y.; Plu,J.; Xu, C.; Scao, T. L.; Gugger, S.; Drame, M.; Lhoest, Q.;and Rush, A. M. 2020. HuggingFace’s Transformers: State-of-the-art Natural Language Processing. arXiv:1910.03771.




Wood, D.; Lublinsky, B.; Roytman, A.; Singh, S.; Adam,C.; Adebayo, A.; An, S.; Chang, Y. C.; Dang, X.-H.; Desai,N.; Dolfi, M.; Emami-Gohari, H.; Eres, R.; Goto, T.; Joshi,D.; Koyfman, Y.; Nassar, M.; Patel, H.; Selvam, P.; Shah,Y.; Surendran, S.; Tsuzuku, D.; Zerfos, P.; and Daijavad, S.2024. Data-Prep-Kit: getting your data ready for LLM ap-plication development. arXiv:2409.18164.




Zhao, Y.; Lv, W.; Xu, S.; Wei, J.; Wang, G.; Dang, Q.; Liu,Y.; and Chen, J. 2023. DETRs Beat YOLOs on Real-timeObject Detection. arXiv:2304.08069.




Zhong, X. 2020. Image-based table recognition: data,model, and evaluation. arXiv:1911.10683.


1https://github.com/DS4SD/docling/discussions/categories/roadmap