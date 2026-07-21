use File::Basename;

# Track Main, Acronym, AND Symbol extensions
push @generated_exts, 'glo', 'gls', 'glg';
push @generated_exts, 'acn', 'acr', 'alg';
push @generated_exts, 'slo', 'sls', 'slg'; # <-- The symbol files!
$clean_ext .= " acr acn alg glo gls glg slo sls slg";

# Add custom dependencies so latexmk knows to build each list type
add_cus_dep('glo', 'gls', 0, 'makeglossaries');
add_cus_dep('acn', 'acr', 0, 'makeglossaries');
add_cus_dep('slo', 'sls', 0, 'makeglossaries'); # <-- The symbol dependency!

# The bulletproof subroutine
sub makeglossaries {
    my ($base_name, $path) = fileparse( $_[0] );
    system("makeglossaries -d \"$path\" \"$base_name\"");
}