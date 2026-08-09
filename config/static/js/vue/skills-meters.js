(function () {
    "use strict";
    if (typeof Vue === "undefined") return;

    function mountSkills(el) {
        var dataScript = el.querySelector('script[type="application/json"]');
        if (!dataScript) return;

        var groups;
        try {
            groups = JSON.parse(dataScript.textContent);
        } catch (e) {
            return;
        }
        if (!groups || !groups.length) return;

        var showLevels = el.dataset.showLevels === "1";

        var app = Vue.createApp({
            data: function () {
                return {
                    groups: groups,
                    activeIndex: 0,
                    showLevels: showLevels,
                    visible: false,
                };
            },
            mounted: function () {
                var self = this;
                if (!("IntersectionObserver" in window)) {
                    self.visible = true;
                    return;
                }
                var observer = new IntersectionObserver(
                    function (entries) {
                        if (entries[0].isIntersecting) {
                            self.visible = true;
                            observer.disconnect();
                        }
                    },
                    { threshold: 0.2 }
                );
                observer.observe(el);
            },
            template:
                '<div>' +
                '  <div class="skills-tabs" v-if="groups.length > 1">' +
                '    <button type="button" class="skills-tab" v-for="(group, index) in groups" :key="group.name" ' +
                '      :class="{ \'is-active\': index === activeIndex }" @click="activeIndex = index">' +
                '      {{ group.name }}' +
                '    </button>' +
                '  </div>' +
                '  <div class="skills-group" v-for="(group, index) in groups" :key="group.name" v-show="groups.length === 1 || index === activeIndex">' +
                '    <ul class="skills-group__list">' +
                '      <li class="skill" v-for="skill in group.skills" :key="skill.name">' +
                '        <div class="skill__row">' +
                '          <span class="skill__name">{{ skill.name }}</span>' +
                '          <span class="skill__note" v-if="skill.note">{{ skill.note }}</span>' +
                '        </div>' +
                '        <div class="skill__meter" v-if="showLevels">' +
                '          <span :style="{ width: (visible ? skill.level * 20 : 0) + \'%\' }"></span>' +
                '        </div>' +
                '      </li>' +
                '    </ul>' +
                '  </div>' +
                '</div>',
        });

        var fallback = el.querySelector("[data-skills-fallback]");
        if (fallback) fallback.remove();

        var mountPoint = document.createElement("div");
        el.appendChild(mountPoint);
        app.mount(mountPoint);
    }

    window.mountSkillsMeters = function () {
        document.querySelectorAll('[data-vue-app="skills-meters"]').forEach(mountSkills);
    };
})();
