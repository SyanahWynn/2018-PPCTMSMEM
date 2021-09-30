%% BEHAVIORAL ANALYSES FamRecRTMS
close all
clear 
warning('off','all');

cd LOCATION OF THE SCRIPT

%% VARIABLES
inputfile_dir   = 'LOCATION OF THE DATA'; %location of inputfile
outputfile      = 'LOCATION AND NAME OF THE OUTPUT FILE'; %location of outputfile
input_ext       = '.csv'; %extension of inputfiles
ppns            = 101:1:120; % participant numbers
sessions        = {'_session_1','_session_2'}; % session names
phases          = {'_enc','_ret'}; % phase names
file_format     = {'%f%s%f%s%f%s%f%f%s','%f%s%f%s%f%f%s%f%f%s%f%f%f'}; % file format of phase input files
vars            = [{'ppn','gender','age','enc_word','enc_ses','enc_resp','enc_RT','fix_time','stim_order','','','',''};...
                    {'ppn','gender','age','ret_word','ret_ses','on_class','on_resp','on_RT','on_acc','conf_resp','conf_RT','conf_rating','fix_time'}];
folder          = 'LOCATION OF THE ANALYSIS FOLDER';
exp_name        = 'RTMS';
stimulations    = {'AngularGyrus','Vertex'};
bins            = 1;
preproc         = true; % do the "preprocessing" or not

%% CREATE FILE LIST
csvdir      = fullfile(inputfile_dir, '*.csv');
csvdf       = dir(csvdir);
csvfiles    = {csvdf.name};

%% LOOP OVER PARTICIPANTS
for p=1:length(csvfiles)/4
    cur_ppn = num2str(ppns(p));
    fprintf('\nPARTICIPANT: %s',cur_ppn)
    % select files of this participant
    ppnfiles = csvfiles(logical(contains(csvfiles,cur_ppn)));    
    for cur_ses=1:length(sessions)
        fprintf('SESSION: %d\n',cur_ses)
        % select the files for this session
        sesfiles = ppnfiles(logical(~cellfun('isempty',strfind(ppnfiles,sessions{cur_ses}))));
        %ppn.hand = handedness(p);
        for cur_phase=1:length(phases)
            % select the files for this memory phase
            phafile = sesfiles(logical(~cellfun('isempty',strfind(sesfiles,phases{cur_phase}))));

            %% LOAD FILE
            inputdir = fullfile(inputfile_dir,phafile);
            fid = fopen(inputdir{:},'rt');
            if fid~=-1
                T = textscan(fid, file_format{cur_phase}, 'Delimiter', ',', 'HeaderLines', 21); % skip practice
            else
                error('Cannot open %s\n',inputdir);
            end
            fclose(fid);
            clear inputdir
            clear fid         

            %% GET THE VARIABLES
            for i=1:length(T)
                evalc(sprintf('ppn.%s = T{i};',vars{cur_phase,i}));
                evalc(sprintf('cur_ppn_var = ppn.%s;',vars{cur_phase,i}));
                while length(cur_ppn_var) > 900
                    evalc(sprintf('ppn.%s(1:20) = [];',vars{cur_phase,i}));
                    cur_ppn_var(1:20) = []; % just for the while loop
                end
            end
            clear T
            clear i
            clear memfiles    

            %% RECODE VARIABLES
            % gender
            if ppn.gender{1} == 'f'
                ppn.gender = 1;
            elseif ppn.gender{1} == 'm'
                ppn.gender = 2;
            end
            % name
            ppn.ppn = ppn.ppn(1);
            % age
            ppn.age = ppn.age(1);
            % session
            ppn.enc_ses = ppn.enc_ses(1);
            % encoding response
            if cur_phase==1
                ppn.enc_resp(strcmp(ppn.enc_resp,'left'))={1}; % pleasant
                ppn.enc_resp(strcmp(ppn.enc_resp,'right'))={2}; % unpleasant
                ppn.enc_resp(strcmp(ppn.enc_resp,''))={9}; % no response
                ppn.enc_resp=cell2mat(ppn.enc_resp);
            end
            % stimulation
            if cur_phase==1
                if strcmp(ppn.stim_order{1},'AV') && cur_ses == 1
                    ppn.cur_stim = stimulations(1); %Angular gyrus
                elseif strcmp(ppn.stim_order{1},'AV') && cur_ses == 2
                    ppn.cur_stim = stimulations(2); %Vertex sham 
                elseif strcmp(ppn.stim_order{1},'VA') && cur_ses == 1
                    ppn.cur_stim = stimulations(2); %Vertex sham
                elseif strcmp(ppn.stim_order{1},'VA') && cur_ses == 2
                    ppn.cur_stim = stimulations(1); %Angular gyrus   
                end
            end
            % retrieval
            if cur_phase==2
                ppn.ret_resp = ppn.on_resp;
                ppn.ret_RT = ppn.on_RT;
                % session
                ppn.ret_ses = ppn.ret_ses(1);
            end

            % loop over bins
            ppn_org = ppn;
            for bin=1:bins
                if cur_phase==2 % only bin retrieval data
                    % check if binning is possible
                    trls = length(ppn_org.fix_time);
                    if mod(trls/bins,1)~=0
                        error('choose a diffent amount of bins')
                    else
                       fprintf('%d bin(s)',bins)
                       fprintf('%d trials per bin',trls/bins)
                    end
                    fldnms = fieldnames(ppn_org);
                    for fld=1:length(fldnms)
                        if length(eval(sprintf('ppn_org.%s',fldnms{fld})))==trls
                            evalc(sprintf('ppn.%s = ppn_org.%s(%d:%d);',fldnms{fld},fldnms{fld},trls/bins*(bin-1)+1,trls/bins*bin));
                        end
                    end
                end

                %% ANALYSES

                % Encoding/Retrieval No Responses
                if cur_phase==1
                    evalc(sprintf('ppn.%s_noresp = sum(ppn.%s_RT(:)==0)',phases{cur_phase}(2:end),phases{cur_phase}(2:end)));
                elseif cur_phase==2
                    evalc(sprintf('ppn.%s_noresp = numel(find(ppn.conf_rating==99))',phases{cur_phase}(2:end)));
                end

                % Encoding pleasantness ratings
                if cur_phase==1
                    ppn.count_pleasant = sum(ppn.enc_resp==1); %pleasant
                    ppn.count_unpleasant = sum(ppn.enc_resp==2); %unpleasant
                    ppn.pleasant_rate= ppn.count_pleasant/(ppn.count_pleasant+ppn.count_unpleasant);
                end

                % Retrieval RTs (6 levels of confidence & 4 memory score groups)
                evalc(sprintf('ppn.%s_RT(ppn.%s_RT==0) = NaN',phases{cur_phase}(2:end),phases{cur_phase}(2:end)));
                
                if cur_phase==2

                    clear hitrp hitrn missrp missrn

                    % confidence levels
                    evalc(sprintf('ppn.%s_meanRT_nso = nanmean(ppn.%s_RT(logical(ppn.conf_rating==11)))',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); % not sure old
                    evalc(sprintf('ppn.%s_meanRT_bso = nanmean(ppn.%s_RT(logical(ppn.conf_rating==12)))',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); % bit sure old
                    evalc(sprintf('ppn.%s_meanRT_vso = nanmean(ppn.%s_RT(logical(ppn.conf_rating==13)))',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); % very sure old
                    evalc(sprintf('ppn.%s_meanRT_nsn = nanmean(ppn.%s_RT(logical(ppn.conf_rating==21)))',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); % not sure new
                    evalc(sprintf('ppn.%s_meanRT_bsn = nanmean(ppn.%s_RT(logical(ppn.conf_rating==22)))',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); % bit sure new
                    evalc(sprintf('ppn.%s_meanRT_vsn = nanmean(ppn.%s_RT(logical(ppn.conf_rating==23)))',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); % very sure new

                    % memory score groups
                    evalc(sprintf('ppn.%s_meanRT_hit = nanmean(ppn.%s_RT(logical(ppn.on_acc==11)))',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); % hit
                    evalc(sprintf('ppn.%s_meanRT_miss = nanmean(ppn.%s_RT(logical(ppn.on_acc==12)))',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); % miss
                    evalc(sprintf('ppn.%s_meanRT_fa = nanmean(ppn.%s_RT(logical(ppn.on_acc==21)))',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); % false alarm
                    evalc(sprintf('ppn.%s_meanRT_cj = nanmean(ppn.%s_RT(logical(ppn.on_acc==22)))',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); % correct rejection

                    % Retrieval counts (6 levels of confidence & 4 memory score groups)
                    ppn.count_vso = sum(logical(ppn.conf_rating == 13)); % very conf old
                    ppn.count_bso = sum(logical(ppn.conf_rating == 12)); % bit conf old
                    ppn.count_nso = sum(logical(ppn.conf_rating == 11)); % not conf old
                    ppn.count_nsn = sum(logical(ppn.conf_rating == 21)); % not conf new
                    ppn.count_bsn = sum(logical(ppn.conf_rating == 22)); % bit conf new
                    ppn.count_vsn = sum(logical(ppn.conf_rating == 23)); % very conf new

                    % ROC curve Familiarity/Recollection estimate
                    % create scores
                    scores = ppn.conf_rating;
                    scores(scores==13)= 6; % very sure old
                    scores(scores==12)= 5; % bit sure old
                    scores(scores==11)= 4; % not sure old
                    scores(scores==21)= 3; % not sure new
                    scores(scores==22)= 2; % bit sure new
                    scores(scores==23)= 1; % very sure new
                    scores(scores==99)= []; % no response
                    % create labels
                    labels = ppn.on_class(logical(ppn.conf_rating~=99)); % get the values with a response
                    labels(labels==1)= 1; % old
                    labels(labels==2)= 0; % new
                    % run ROC
                    addpath(genpath('ROC'))
                    targf = zeros(1,length(unique(scores))); % frequency matrix for targets
                    luref = zeros(1,length(unique(scores))); % frequency matrix for lures
                    cnt=1;
                    for i=length(unique(scores)):-1:1
                        targf(cnt)=sum(logical(scores==i & labels==1));
                        luref(cnt)=sum(logical(scores==i & labels==0));
                        cnt=cnt+1;
                    end
                    nBins        = size(targf,2); % number of rating bins
                    nConds       = size(targf,1); % number of conditions
                    fitStat      = '-LL'; % fit statistic used (maximum likelihood estimation)
                    model        = 'dpsd'; % dual-process signal detection (DPSD) model 
                    ParNames     = {'Ro' 'Rn' 'F'};
                    [x0,LB,UB]   = gen_pars(model,nBins,nConds,ParNames);
                    % optional
                    subID        = num2str(ppn.ppn);
                    groupID      = 'N/A';
                    condLabels   = {'N/A'};
                    modelID      = 'dpsd model 1';
                    outpath = fullfile(folder,num2str(ppn.ppn));
                    mkdir(outpath)
                    rocData      = roc_solver(targf,luref,model,fitStat,x0,LB,UB, ...
                        'groupID',ppn.cur_stim{:}, ...
                        'subID',subID, ...
                        'condLabels',condLabels, ...
                        'modelID',modelID, ... 
                        'saveFig',outpath, ...
                        'figTimeout',1);
                    ppn.hit_rate = rocData.observed_data.accuracy_measures.HR;
                    ppn.fa_rate = rocData.observed_data.accuracy_measures.FAR;
                    ppn.d_prime = rocData.observed_data.accuracy_measures.Dprime;
                    ppn.rec = rocData.dpsd_model.parameters.Ro;
                    ppn.recnew = rocData.dpsd_model.parameters.Rn;
                    ppn.fam = rocData.dpsd_model.parameters.F;
                    ppn.c1 = rocData.dpsd_model.parameters.criterion(1);
                    ppn.c2 = rocData.dpsd_model.parameters.criterion(2);
                    ppn.c3 = rocData.dpsd_model.parameters.criterion(3);
                    ppn.c4 = rocData.dpsd_model.parameters.criterion(4);
                    ppn.c5 = rocData.dpsd_model.parameters.criterion(5);
                    ppn.c = rocData.observed_data.bias_measures.c;
                    ppn.beta = rocData.observed_data.bias_measures.beta;
                    ppn.hr_vso = rocData.observed_data.target.proportions(1);
                    ppn.hr_bso = rocData.observed_data.target.proportions(2);
                    ppn.hr_nso = rocData.observed_data.target.proportions(3);
                    ppn.cj_vsn = rocData.observed_data.target.proportions(6);
                    ppn.cj_bsn = rocData.observed_data.target.proportions(5);
                    ppn.cj_nsn = rocData.observed_data.target.proportions(4);

                    if p==1
                        evalc(sprintf('tot_targf%s = targf;',sessions{cur_ses}));
                        evalc(sprintf('tot_luref%s = luref;',sessions{cur_ses}));
                        evalc(sprintf('tot_targf_%s = targf;',ppn.cur_stim{:}));
                        evalc(sprintf('tot_luref_%s = luref;',ppn.cur_stim{:}));
                    else
                        evalc(sprintf('tot_targf%s = tot_targf%s+targf;',sessions{cur_ses},sessions{cur_ses}));
                        evalc(sprintf('tot_luref%s = tot_luref%s+luref;',sessions{cur_ses},sessions{cur_ses}));
                        evalc(sprintf('tot_targf_%s = tot_targf_%s+targf;',ppn.cur_stim{:},ppn.cur_stim{:}));
                        evalc(sprintf('tot_luref_%s = tot_luref_%s+luref;',ppn.cur_stim{:},ppn.cur_stim{:}));
                    end  

                    clear scores
                    clear labels
                    clear x

                    clear targf luref nBins nConds fitStat model ParNames x0 LB UB subID groupID
                    clear condLabels modelID outpath roc_solver
                end
                % RT
                evalc(sprintf('ppn.%s_RT = nanmean(ppn.%s_RT)',phases{cur_phase}(2:end),phases{cur_phase}(2:end))); 

                if cur_phase==2 && bins~=1 % only bin retrieval data
                    evalc(sprintf('ppn_bin%d=ppn;',bin));
                end
            end

        end
        clear cur_phase
        clear sesfiles
        clear phafile

        if bins ~= 1
            for bin=1:bins
                evalc(sprintf('ppn=ppn_bin%d',bin))
                ppn=rmfield(ppn,{'enc_word','enc_resp','fix_time',...
                'ret_word','on_class','on_resp','on_RT','on_acc','stim_order'...
                'ret_resp','conf_resp','conf_RT','conf_rating'});

                curtable=struct2table(ppn);

                if p==1
                    evalc(sprintf('table_behav%s_%d = curtable;',sessions{cur_ses},bin));
                    evalc(sprintf('table_roc%s_%d = rocData;',sessions{cur_ses},bin));
                    evalc(sprintf('table_behav_%s_%d = curtable;',ppn.cur_stim{:},bin));
                    evalc(sprintf('table_roc_%s_%d = rocData;',ppn.cur_stim{:},bin));
                else
                    evalc(sprintf('table_behav%s_%d = [table_behav%s_%d;curtable];',sessions{cur_ses},bin,sessions{cur_ses},bin));
                    evalc(sprintf('table_roc%s_%d = [table_roc%s_%d;rocData];',sessions{cur_ses},bin,sessions{cur_ses},bin));
                    evalc(sprintf('table_behav_%s_%d = [table_behav_%s_%d;curtable];',ppn.cur_stim{:},bin,ppn.cur_stim{:},bin));
                    evalc(sprintf('table_roc_%s_%d = [table_roc_%s_%d;rocData];',ppn.cur_stim{:},bin,ppn.cur_stim{:},bin));
                end
            end
        else
            ppn=rmfield(ppn,{'enc_word','enc_resp','fix_time',...
            'ret_word','on_class','on_resp','on_RT','on_acc','stim_order'...
            'ret_resp','conf_resp','conf_RT','conf_rating'});

            curtable=struct2table(ppn);

            if p==1
                evalc(sprintf('table_behav%s = curtable;',sessions{cur_ses}));
                evalc(sprintf('table_roc%s = rocData;',sessions{cur_ses}));
                evalc(sprintf('table_behav_%s = curtable;',ppn.cur_stim{:}));
                evalc(sprintf('table_roc_%s = rocData;',ppn.cur_stim{:}));
            else
                evalc(sprintf('table_behav%s = [table_behav%s;curtable];',sessions{cur_ses},sessions{cur_ses}));
                evalc(sprintf('table_roc%s = [table_roc%s;rocData];',sessions{cur_ses},sessions{cur_ses}));
                evalc(sprintf('table_behav_%s = [table_behav_%s;curtable];',ppn.cur_stim{:},ppn.cur_stim{:}));
                evalc(sprintf('table_roc_%s = [table_roc_%s;rocData];',ppn.cur_stim{:},ppn.cur_stim{:}));
            end
        end
    end
    clear ppnfiles cur_ppn
    clear cur_ses
    clear ppn ppn_org
end
clear csv*
clear cur_ppn
clear p i 

if bins ~= 1
    for i=1:length(sessions)
        for bin=1:bins
            evalc(sprintf('Data.BehavRes%s.bins%d.bin%d = table_behav%s_%d;',sessions{i},bins,bin,sessions{i},bin));
        end
    end

    for i=1:length(stimulations)
        for bin=1:bins
            evalc(sprintf('Data.BehavRes_%s.bins%d.bin%d = table_behav_%s_%d;',stimulations{i},bins,bin,stimulations{i},bin));
        end
    end
else
    for i=1:length(sessions)
        evalc(sprintf('Data.BehavRes%s = table_behav%s;',sessions{i},sessions{i}));
    end

    for i=1:length(stimulations)
        evalc(sprintf('Data.BehavRes_%s = table_behav_%s;',stimulations{i},stimulations{i}));
    end
end

% save(outputfile,'Results')
save(outputfile,'Data')

clear inputfile_dir 
clear stimulations conf
clear input_ext i
clear ppns tot* cnt
clear sessions exp_name
clear phases table*   
clear file_format curtable
clear vars curl rocData
clear table_behav folder
clear targf luref nBins nConds fitStat model ParNames x0 LB UB subID groupID
clear condLabels modelID outpath roc_solver