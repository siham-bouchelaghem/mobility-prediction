#!/usr/bin/env perl

# USAGE: ./fold.pl 6 datasets/dataset1.csv > datasets/dataset6.csv

use strict;

my %h;
my $k = $ARGV[0];
open my $FH, '<', $ARGV[1];
while (<$FH>){
    chop;
    my @F = split ',';
    push (@{$h{$F[0]}}, $F[1]);
    if (@{$h{$F[0]}}==$k) {
        printf "%s,%s\n", $F[0],join(',', @{$h{$F[0]}}); 
        shift @{$h{$F[0]}};
    } 
}
