/* eslint-env node */

'use strict';

module.exports = function (grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        sass: {
            dist: {
                options: {
                    outputStyle: 'compressed',
                    sourceMap: true,
                },
                files: {
                    'static/styles/css/base.css': 'static/styles/base.scss',
                    'static/styles/css/index.css': 'static/styles/index.scss',
                    'static/styles/css/reservations.css': 'static/styles/reservations.scss',
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
                    'static/scripts/dist/reservations.js': 'static/scripts/reservations.js',
                },
            },
        },
        eslint: {
            options: {
                configFile: '.eslintrc.json',
            },
            target: ['static/scripts/base.js'],
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
                src: ['templates/base.html', 'templates/index.html', 'templates/reservations.html'],
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
