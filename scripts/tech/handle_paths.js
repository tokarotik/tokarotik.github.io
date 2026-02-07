let PATH_404_PAGE = "/pages/tech/404.html";
let PAGES_LIST = [
    "beauty",
    "index-demo"
]

function is_in_pages_list(path) {
    return PAGES_LIST.includes(path.slice(1));
}

function handle_paths() {
    let path = location.pathname;
    var to_direct = PATH_404_PAGE;
    if(path == "/") {
        to_direct = "/index.html";
    }
    if(is_in_pages_list(path)) {
        to_direct = path;
    }
    console.log("Path: " + path);
    console.log("Direct to: " + to_direct);
    return to_direct;
}

// Export the function as default
export default handle_paths;