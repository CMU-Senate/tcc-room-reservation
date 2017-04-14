/* eslint-env node */

'use strict';

const
    scripts = ['base.js', 'reservations.js'],
    styles = ['base.scss', 'index.scss', 'reservations.scss'],
    templates = ['base.html', 'index.html', 'reservations.html'];

module.exports = function (grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        sass: {
            dist: {
                options: {
                    outputStyle: 'compressed',
                    sourceMap: true,
                },
                files: styles.reduce((acc, x) => {
                    acc[`static/styles/css/${x.replace('.scss', '.css')}`] = `static/styles/${x}`;

                    return acc;
                }, {}),
            },
        },
        babel: {
            options: {
                sourceMap: true,
            },
            dist: {
                files: scripts.reduce((acc, x) => {
                    acc[`static/scripts/dist/${x}`] = `static/scripts/${x}`;

                    return acc;
                }, {}),
            },
        },
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
        watch: {
            css: {
                files: 'static/styles/*.scss',
                tasks: ['sass'],
            },
            js: {
                files: 'static/scripts/*.js',
                tasks: ['babel'],
            },
        },
    });

    grunt.loadNpmTasks('gruntify-eslint');
    grunt.loadNpmTasks('grunt-sass-lint');
    grunt.loadNpmTasks('grunt-htmlhint');
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-babel');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('default', ['sass', 'eslint', 'sasslint', 'htmlhint', 'babel']);
};
