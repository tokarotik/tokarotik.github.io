/**
 * Complete router with page-specific resource paths
 */

const CONFIG = {
    notFoundPage: "/pages/tech/404.html",
    pagesList: ["beauty", "index-demo"],
    pagesDirectory: "/pages/"
};

function handle_paths(customPath = null) {
    const path = customPath || window.location.pathname;
    
    if (path === "/") {
        return "/index.html";
    }
    
    const pageName = path.startsWith("/") ? path.slice(1) : path;
    
    if (CONFIG.pagesList.includes(pageName)) {
        return CONFIG.pagesDirectory + pageName + ".html";
    }
    
    return CONFIG.notFoundPage;
}

/**
 * Replace all /styles/, /scripts/libs/, /images/ with page-specific paths
 */
function replaceIframeLinks(iframeId) {
    const iframe = document.getElementById(iframeId);
    
    if (!iframe) {
        console.error(`Iframe #${iframeId} not found`);
        return;
    }
    
    iframe.addEventListener('load', function() {
        try {
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            
            if (!iframeDoc) {
                console.error("Cannot access iframe (CORS)");
                return;
            }
            
            // Extract current page name from iframe src
            // Example: /pages/beauty.html -> beauty
            const srcUrl = iframe.src;
            const pageMatch = srcUrl.match(/\/pages\/([^\/]+)\.html/);
            
            if (!pageMatch) {
                console.log("Cannot determine page name from:", srcUrl);
                return;
            }
            
            const pageName = pageMatch[1];
            const pageBasePath = `/pages/${pageName}/`;
            
            console.log(`📄 Processing page: ${pageName}`);
            
            // Get current HTML
            const originalHtml = iframeDoc.documentElement.outerHTML;
            let modifiedHtml = originalHtml;
            
            // Replace /styles/ -> /pages/{pageName}/styles/
            modifiedHtml = modifiedHtml.replace(
                /href=["']\/styles\//g, 
                `href="${pageBasePath}styles/`
            );
            modifiedHtml = modifiedHtml.replace(
                /src=["']\/styles\//g, 
                `src="${pageBasePath}styles/`
            );
            
            // Replace /scripts/libs/ -> /pages/{pageName}/scripts/libs/
            modifiedHtml = modifiedHtml.replace(
                /src=["']\/scripts\/libs\//g, 
                `src="${pageBasePath}scripts/libs/`
            );
            
            // Replace /images/ -> /pages/{pageName}/images/
            modifiedHtml = modifiedHtml.replace(
                /src=["']\/images\//g, 
                `src="${pageBasePath}images/`
            );
            modifiedHtml = modifiedHtml.replace(
                /href=["']\/images\//g, 
                `href="${pageBasePath}images/`
            );
            
            // Rewrite the document if changes were made
            if (originalHtml !== modifiedHtml) {
                console.log(`✓ Replacing paths with ${pageBasePath}...`);
                iframeDoc.open();
                iframeDoc.write(modifiedHtml);
                iframeDoc.close();
                console.log("✓ Done");
            } else {
                console.log("✓ No path replacements needed");
            }
            
        } catch (error) {
            console.error("Error processing iframe:", error);
        }
    });
}

function initRouter(iframeId) {
    const iframe = document.getElementById(iframeId);
    
    if (!iframe) {
        console.error(`Iframe #${iframeId} not found`);
        return;
    }
    
    iframe.src = handle_paths();
    replaceIframeLinks(iframeId);
    
    console.log("✓ Router initialized");
}

export { handle_paths, replaceIframeLinks, initRouter };
export default handle_paths;