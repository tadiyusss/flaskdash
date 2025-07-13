const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const openSidebar = document.getElementById('openSidebar');
const closeSidebar = document.getElementById('closeSidebar');

function showSidebar() {
    sidebar.classList.remove('-translate-x-full');
    sidebarOverlay.classList.remove('hidden');
}
function hideSidebar() {
    sidebar.classList.add('-translate-x-full');
    sidebarOverlay.classList.add('hidden');
}

if (openSidebar) {
    openSidebar.addEventListener('click', showSidebar);
}
if (closeSidebar) {
    closeSidebar.addEventListener('click', hideSidebar);
}
if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', hideSidebar);
}