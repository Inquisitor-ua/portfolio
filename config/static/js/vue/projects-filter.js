(function () {
    "use strict";
    if (typeof Vue === "undefined") return;

    function mountFilter(el) {
        var section = el.closest(".projects-section");
        var grid = section ? section.querySelector("[data-project-grid]") : null;
        if (!grid) return;

        var cards = Array.prototype.slice.call(grid.querySelectorAll("[data-project-card]"));
        var techSet = new Set();
        cards.forEach(function (card) {
            (card.dataset.tech || "").split(",").forEach(function (t) {
                t = t.trim();
                if (t) techSet.add(t);
            });
        });
        var technologies = Array.from(techSet).sort();
        if (!cards.length) return;

        var app = Vue.createApp({
            data: function () {
                return {
                    query: "",
                    technologies: technologies,
                    activeTech: [],
                    visibleCount: cards.length,
                };
            },
            watch: {
                query: function () {
                    this.applyFilter();
                },
                activeTech: {
                    handler: function () {
                        this.applyFilter();
                    },
                    deep: true,
                },
            },
            methods: {
                toggleTech: function (tech) {
                    var idx = this.activeTech.indexOf(tech);
                    if (idx === -1) this.activeTech.push(tech);
                    else this.activeTech.splice(idx, 1);
                },
                applyFilter: function () {
                    var query = this.query.trim().toLowerCase();
                    var active = this.activeTech;
                    var visibleCount = 0;
                    cards.forEach(function (card) {
                        var title = card.dataset.title || "";
                        var tech = (card.dataset.tech || "").split(",");
                        var matchesQuery = !query || title.indexOf(query) !== -1;
                        var matchesTech =
                            !active.length ||
                            active.every(function (t) {
                                return tech.indexOf(t) !== -1;
                            });
                        var visible = matchesQuery && matchesTech;
                        card.classList.toggle("is-hidden", !visible);
                        if (visible) visibleCount++;
                    });
                    this.visibleCount = visibleCount;
                },
            },
            template:
                '<div>' +
                '  <label class="projects-filter__search">' +
                '    <svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg>' +
                '    <input type="search" v-model="query" placeholder="Search projects…" aria-label="Search projects">' +
                '  </label>' +
                '  <div class="projects-filter__tags" v-if="technologies.length">' +
                '    <button type="button" class="projects-filter__tag" v-for="tech in technologies" :key="tech" ' +
                '      :class="{ \'is-active\': activeTech.includes(tech) }" @click="toggleTech(tech)">' +
                '      {{ tech }}' +
                '    </button>' +
                '  </div>' +
                '  <p class="projects-filter__empty" v-show="visibleCount === 0">No projects match your filters.</p>' +
                '</div>',
        });

        el.innerHTML = "";
        app.mount(el);
    }

    window.mountProjectsFilter = function () {
        document.querySelectorAll('[data-vue-app="projects-filter"]').forEach(mountFilter);
    };
})();
