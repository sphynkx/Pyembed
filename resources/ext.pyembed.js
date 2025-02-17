document.addEventListener('readystatechange', function () {
    if (document.readyState === 'complete') {
        const pres = document.querySelectorAll('pre.line-numbers');

        pres.forEach(pre => {            
                const codeBlock = pre.querySelector('code.language-python');
                if (codeBlock) {
                    codeBlock.classList.add('prism-code');
                    codeBlock.dataset.lineNumbered = true;

                    if (typeof Prism !== 'undefined') {
                        Prism.highlightElement(codeBlock);
                    } else {
                        console.error('Prism is not defined');
                    }

                    const lines = codeBlock.innerHTML.split('\n');
                    const numberedLines = lines.map(line => `<span class="linenum"></span>${line}`);
                    codeBlock.innerHTML = numberedLines.join('\n');
                }
        });
    }
});
