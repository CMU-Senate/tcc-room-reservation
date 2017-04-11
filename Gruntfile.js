/* eslint-env node */

'use strict';

module.exports = function (grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        sass: {
            dist: {
                options: {
                    outputStyle: 'expanded',
                    sourceMap: true,
                },
                files: {
                    'static/styles/css/base.css': 'static/styles/base.scss',
                    'static/styles/css/index.css': 'static/styles/index.scss',
                },
            },
        },
        babel: {
            options: {
                sourceMap: true,
            },
            dist: {
                files: {
                    'static/scripts/dist/base.js': 'static/scripts/base.js',
                },
            },
        },
        eslint: {
            options: {
                configFile: '.eslintrc.json',
            },
            target: ['static/scripts/base.js'],
        },
        scsslint: {
            allFiles: [
                'static/styles/base.scss',
            ],
            options: {
                config: '.scss-lint.yml',
            },
        },
        htmlhint: {
            options: {
                htmlhintrc: '.htmlhintrc',
            },
            html1: {
                src: ['templates/base.html', 'templates/index.html'],
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
    grunt.loadNpmTasks('grunt-scss-lint');
    grunt.loadNpmTasks('grunt-htmlhint');
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-babel');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('default', ['sass', 'eslint', 'scsslint', 'htmlhint', 'babel']);
};
