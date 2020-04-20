function createSVG(pitching_json, batting_json, other_json, def_json, ind_pit_json, bat_splits, pit_splits){
    const width = 400;
    const max_bar_height = 240;
    const svg_height = 200;
    const def_svg_height = 275;
    const default_left_margin = 50;
    const splits_left_margin = 80;
    const bar_sep = 5;
    const bar_width = 30;

    function fillColor(rat){
        if (rat > 70){
            return '#44bbdd';
        }
        else if (rat > 55){
            return '#117722';
        }
        else if (rat > 40){
            return '#eac117';
        }
        else if (rat > 25){
            return '#dd8033';
        }
        else {
            return '#dd0000';
        }
    }

    function addRatingBars(to_append, col_name, opacity, stroke_width, is_splits){
        to_append.attr('height', bar_width)
                 .attr('width', function(d){return 3*d[col_name];})
                 .attr('x', is_splits ? splits_left_margin : default_left_margin)
                 .attr('y', function(d, i){return i*(bar_width + bar_sep);})
                 .attr('fill', function(d){return fillColor(d[col_name]);})
                 .attr('stroke', 'black')
                 .attr('stroke-width', stroke_width)
                 .style('opacity', opacity);
    }

    function addRatingText(to_append, col_name, left_offset, add_slash, is_splits){
        to_append.text(function(d){return add_slash ? '/' + d[col_name] : d[col_name]})
                 .attr('x', is_splits ? splits_left_margin + left_offset : default_left_margin + left_offset)
                 .attr('y', function(d, i){return (i+0.6)*(bar_width + bar_sep);})
                 .attr('fill', function(d){return fillColor(d[col_name])});
    }

    function createRatingPlot(svg, ratings, has_potentials, is_splits){
        let bar_backgrounds = svg.selectAll('rect.backgrounds')
                                .data(ratings)
                                .enter()
                                .append('rect');

        bar_backgrounds.attr('height', bar_width)
                       .attr('width', max_bar_height)
                       .attr('x', is_splits ? splits_left_margin : default_left_margin)
                       .attr('y', function(d, i){return i*(bar_width + bar_sep);})
                       .attr('fill', 'lightgray');

        if (has_potentials) {
            let pot_bars = svg.selectAll('rect.potentials')
                              .data(ratings)
                              .enter()
                              .append('rect');
            addRatingBars(pot_bars, 'potential', 0.6, 1, is_splits);

            let pot_bar_values = svg.selectAll('text.potentials')
                                    .data(ratings)
                                    .enter()
                                    .append('text');
            addRatingText(pot_bar_values, 'potential', 270, true, is_splits);
        }

        let cur_bars = svg.selectAll('rect.currents')
                          .data(ratings)
                          .enter()
                          .append('rect');
        addRatingBars(cur_bars, 'current', 2, 2, is_splits);

        let cur_bar_labs = svg.selectAll('text.indexs')
                              .data(ratings)
                              .enter()
                              .append('text');

        cur_bar_labs.text(function(d){return d['index'];})
                    .attr('x', 0)
                    .attr('y', function(d, i){return (i+0.6)*(bar_width + bar_sep);});

        let cur_bar_values = svg.selectAll('text.currents')
                                .data(ratings)
                                .enter()
                                .append('text');

        addRatingText(cur_bar_values, 'current', 250, false, is_splits);
    }

    function addRatings(selected_div, ratings, svg_height, has_potentials, is_splits){
        let svg = selected_div.append('div')
                              .attr('class', 'col-md-auto')
                              .append('svg')
                              .attr('width', width)
                              .attr('height', svg_height);

        createRatingPlot(svg, ratings, has_potentials, is_splits);
    }

    let ratings_div = d3.select('#ratings');
    addRatings(ratings_div, batting_json, svg_height, true, false);
    addRatings(ratings_div, pitching_json, svg_height, true, false);
    addRatings(ratings_div, other_json, svg_height, true, false);
    addRatings(ratings_div, def_json, def_svg_height, true, false);
    addRatings(ratings_div, ind_pit_json, svg_height, true, false);

    let splits_div = d3.select('#splits-ratings');
    addRatings(splits_div, bat_splits['r'], svg_height, false, true);
    addRatings(splits_div, bat_splits['l'], svg_height, false, true);
    addRatings(splits_div, pit_splits['r'], svg_height, false, true);
    addRatings(splits_div, pit_splits['l'], svg_height, false, true);
}

