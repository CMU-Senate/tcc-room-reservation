/* eslint-env node */

'use strict';

const
    scripts = ['base.js', 'reservations.js'],
    templates = ['base.html', 'index.html', 'reservations.html', 'contact.html'];

module.exports = function (grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        eslint: {
            options: {
                configFile: '.eslintrc.json',
            },
            target: scripts.map(x => `static/scripts/${x}`),
        },
        sasslint: {
            target: [
                'static/styles/*.scss',
            ],
            options: {
                configFile: '.sass-lint.yml',
            },
        },
        htmlhint: {
            options: {
                htmlhintrc: '.htmlhintrc',
            },
            html1: {
                src: templates.map(x => `templates/${x}`),
            },
        },
    });

    grunt.loadNpmTasks('gruntify-eslint');
    grunt.loadNpmTasks('grunt-sass-lint');
    grunt.loadNpmTasks('grunt-htmlhint');

    grunt.registerTask('default', ['eslint', 'sasslint', 'htmlhint']);
};
